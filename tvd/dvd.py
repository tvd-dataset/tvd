#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013 Hervé BREDIN (http://herve.niderb.fr/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""Utilities for dealing with TV series DVDs"""

import os
import sys
import subprocess
import numpy as np
from lxml import objectify


class DVD(object):
    """

    Parameters
    ----------
    dvd : str, optional
        Path to dumped DVD directory (with "vobcopy -m -o `dvd`").
        Default uses physical DVD.
    lsdvd : str, optional
        Path to `lsdvd` command line tool (default to "lsdvd")
    xml : str or file, optional
        Use XML file precomputed by `lsdvd -Ox -avs`.
        When provided, both `dvd` and `lsdvd` parameters have no effect.
    """

    def __init__(self, dvd=None, lsdvd=None, xml=None):

        super(DVD, self).__init__()

        # path to `lsdvd` command line tool
        if lsdvd is None:
            lsdvd = 'lsdvd'

        # by default `lsdvd` will look for physical DVD
        if dvd is None:
            dvd = ''

        if xml is None:

            # use lsdvd command line tool to extract DVD structure
            # TODO: error handle
            with open(os.devnull, mode='w') as f:
                xml_content = subprocess.check_output(
                    [lsdvd, '-Ox', '-avs', dvd], stderr=f
                )

        elif isinstance(xml, file):

            xml_content = xml.read()

        elif isinstance(xml, str):

            with open(xml, mode='r') as f:
                xml_content = f.read()

        # get rid of potentially buggy characters
        # TODO: find a better fix
        xml_content = xml_content.replace('\xff', '?').replace('&', '')

        # titles sorted in index order
        self.titles = sorted(
            [DVDTitle(t) for t in objectify.fromstring(xml_content).track[:]],
            key=lambda title: title.index,
        )

    def __str__(self):
        import pandas
        LENGTH = 'DURATION'
        AUDIO = 'AUDIO TRACKS'
        SUBTITLE = 'SUBTITLE TRACKS'
        df = pandas.DataFrame(
            index=[t.index for t in self.titles],
            columns=[LENGTH, AUDIO, SUBTITLE]
        )

        for title in self.titles:
            df.ix[title.index, LENGTH] = title.duration / 60.
            df.ix[title.index, AUDIO] = ' '.join([a.langcode for a in title.audios])
            df.ix[title.index, SUBTITLE] = ' '.join([s.langcode for s in title.subtitles])

        return str(df)


class DVDTitle(object):

    def __init__(self, track):
        super(DVDTitle, self).__init__()
        self.index = int(track.ix)
        self.duration = float(track.length)
        if hasattr(track, 'audio'):
            self.audios = [
                DVDAudio(a) for a in track.audio[:]
            ]
        else:
            self.audios = []
        if hasattr(track, 'subp'):
            self.subtitles = [
                DVDSubtitle(s) for s in track.subp[:]
            ]
        else:
            self.subtitles = []

    def __str__(self):
        return "<DVDTitle dvd://%d>" % self.index

    def __repr__(self):
        return "<DVDTitle dvd://%d>" % self.index


class DVDAudio(object):

    def __init__(self, audio):
        super(DVDAudio, self).__init__()
        self.index = int(audio.ix)
        self.language = str(audio.language)
        self.langcode = str(audio.langcode)
        self.frequency = int(audio.frequency)
        self.channel = int(audio.channels)
        self.format = str(audio.format)


class DVDSubtitle(object):

    def __init__(self, subp):
        super(DVDSubtitle, self).__init__()
        self.index = int(subp.ix)
        self.language = str(subp.language)
        self.langcode = str(subp.langcode)


class TVSeriesDVD(DVD):
    """

    Parameters
    ----------
    name : str
        Name of the TV series (e.g. "The Big Bang Theory")
    season : int
        Season number (e.g. 1 for first season)
    first : int
        Episode number ()
    dvd : str, optional
        Path to dumped DVD directory (with "vobcopy -m -o `dvd`").
        Default uses physical DVD.
    lsdvd : str, optional
        Path to `lsdvd` command line tool (default to "lsdvd")
    xml : str or file, optional
        Use XML file precomputed by `lsdvd -Ox -avs`.
        When provided, both `dvd` and `lsdvd` parameters have no effect.
    """
    def __init__(self, name, season, first, dvd=None, lsdvd=None, xml=None):
        super(TVSeriesDVD, self).__init__(dvd=dvd, lsdvd=lsdvd, xml=xml)
        self.name = name
        self.season = season
        self.first = first
        self.tolerance = 0.2

    def guess_episode_duration(self, number=None):
        """Try and guess the average duration of an episode

        This heuristic relies on the following assumptions:
        - there are at least 3 episodes in every DVD
        - episodes are usually among the first tracks of the DVD
        - the very first track may contain the concatenation of all episodes

        Parameters
        ----------
        number : int, optional
            Number of episodes in DVD.

        Returns
        -------
        duration : float
            Average episode duration

        """

        if number is None:
            number = 3

        return np.median([title.duration for title in self.titles[:number+1]])

    def find_episodes(self, duration=None, number=None):
        """

        This heuristic relies on the following assumptions:
        - there are at least 3 episodes in every DVD
        - episodes are usually among the first tracks of the DVD
        - the very first track may contain the concatenation of all episodes
        - episodes are stored in chronological order on the DVD

        Parameters
        ----------
        duration : float, optional
            Average episode duration.
            Try to guess it automatically when not provided.
        number : int, optional
            Number of episodes in DVD.
            Try to guess it automatically when not provided.

        Returns
        -------
        episodes : list of `DVDTitle`
            List of titles found to contain each episodes.
        """

        tolerance = 0.2


        if duration is None:
            target_duration = self.guess_episode_duration(number=number)
        else:
            target_duration = duration

        # duration of first track
        firstDuration = self.titles[0].duration

        print firstDuration
        print target_duration


        # first track is very likely to contain all episodes
        # if its duration is more than 0.8 x the number of episodes
        if (firstDuration/target_duration) > (1-tolerance) * (3 if number is None else number):
            firstTitleContainsAll = True
        else:
            firstTitleContainsAll = False


        episodes = []
        sum_duration = 0.

        for title in self.titles:

            # title duration
            duration = title.duration

            # skip title if its duration is not close enough to target duration
            if np.abs(np.log(duration/target_duration)) > np.log(1+tolerance):
                continue

            if number:
                # stop looking for episodes if we found enough already
                if len(episodes) > number:
                    break

                # do not add this episode if adding it would result
                if firstTitleContainsAll:
                    # skip track if adding it would not match first title duration
                    average_duration = sum_duration / max(1, len(episodes))
                    if (sum_duration + duration) > all_duration + tolerance * average_duration:
                        break

            # if we passed all previous test,
            # then it is an episode
            episodes.append(title)
            sum_duration = sum_duration + title.duration

        return episodes
