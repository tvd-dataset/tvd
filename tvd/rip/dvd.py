#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2015 CNRS
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
# AUTHORS
# Hervé BREDIN -- http://herve.niderb.fr/


from __future__ import unicode_literals

import os
import six
import logging
import subprocess
import numpy as np
from ..core import Episode
from unidecode import unidecode

try:
    from lxml import objectify
except ImportError as e:
    pass


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
        self.dvd = '' if dvd is None else dvd

        if xml is None:

            # use lsdvd command line tool to extract DVD structure
            # TODO: error handle
            with open(os.devnull, mode='w') as f:
                xml_content = subprocess.check_output(
                    [lsdvd, '-Ox', '-avs', self.dvd], stderr=f
                )

        elif isinstance(xml, file):

            xml_content = xml.read()

        elif isinstance(xml, str):

            with open(xml, mode='r') as f:
                xml_content = f.read()

        # get rid of potentially buggy characters
        # TODO: find a better fix

        xml_content = six.u(unidecode(xml_content)).translate({ord(u'&'): None})

        # titles sorted in index order
        self.titles = sorted(
            [DVDTitle(t) for t in objectify.fromstring(str(xml_content)).track[:]],
            key=lambda title: title.index,
        )

    def __repr__(self):
        return '<DVD dvd://{path}>'.format(path=self.dvd)


class DVDTitle(object):

    def __init__(self, track):
        super(DVDTitle, self).__init__()

        self.index = int(track.ix)
        self.duration = float(track.length)

        # load audio tracks
        self.audios = {}
        if hasattr(track, 'audio'):
            for a in track.audio[:]:
                audio = DVDAudio(a)
                if audio.langcode in self.audios:
                    msg = (
                        'Title {index} contains multiple audio tracks '
                        'with language {langcode}.'
                    ).format(index=self.index, langcode=audio.langcode)
                    logging.debug(msg)
                    continue

                self.audios[audio.langcode] = audio

        # load subtitles
        self.subtitles = {}
        if hasattr(track, 'subp'):
            for s in track.subp[:]:
                subtitle = DVDSubtitle(s)
                if subtitle.langcode in self.subtitles:
                    msg = (
                        'Title {index} contains multiple subtitles tracks '
                        'with language {langcode}.'
                    ).format(index=self.index, langcode=subtitle.langcode)
                    logging.debug(msg)
                    continue

                self.subtitles[subtitle.langcode] = subtitle

    def __str__(self):
        return "<DVDTitle dvd://%d>" % self.index

    def __repr__(self):
        return "<DVDTitle dvd://%d>" % self.index

    def iter_audio(self):
        return iter(sorted([
            (audio.index, langcode)
            for langcode, audio in six.iteritems(self.audios)
        ]))

    def iter_subtitles(self):
        return iter(sorted([
            (subtitle.index, langcode)
            for langcode, subtitle in six.iteritems(self.subtitles)
        ]))


# TODO: make it a namedtuple
class DVDAudio(object):

    def __init__(self, audio):
        super(DVDAudio, self).__init__()
        self.index = int(audio.ix)
        self.language = str(audio.language)
        self.langcode = str(audio.langcode)
        self.frequency = int(audio.frequency)
        self.channel = int(audio.channels)
        self.format = str(audio.format)


# TODO: make it a namedtuple
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

    def guess_episode_duration(self, number=None):
        """Try and guess the average duration of an episode

        This heuristic relies on the following assumptions:
        - episodes are usually among the longest tracks of the DVD
        - there are at least 3 episodes in every DVD

        Parameters
        ----------
        number : int, optional
            Number of episodes in DVD.

        Returns
        -------
        duration : float
            Average episode duration

        """

        # if number is not known in advance
        # use 3 by default
        if number is None:
            number = 3

        # sort titles by duration (longest first)
        titles, durations = zip(
            *sorted(
                [(t, t.duration) for t in self.titles],
                key=lambda x: x[1], reverse=True)
        )

        # estimate episode duration as
        # median of n+1 longest titles
        return np.median(durations[:number+1])

    def find_episode_titles(self, duration=None, number=None):
        """

        This heuristic relies on the following assumptions:
        - episodes are usually among the longest tracks of the DVD
        - there are at least 3 episodes in every DVD
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

        if duration is None:
            target_duration = self.guess_episode_duration(number=number)
        else:
            target_duration = duration

        # duration of first track
        firstDuration = self.titles[0].duration

        # first track is very likely to contain all episodes
        # if its duration is more than two times the episode duration
        if firstDuration > 2 * target_duration:
            firstTitleContainsAll = True
        else:
            firstTitleContainsAll = False

        # detected episodes so far and their total duration
        episode_titles = {}
        sum_duration = 0.

        for title in self.titles:

            # title duration
            duration = title.duration

            # skip title if its duration is not close enough to target duration
            if np.abs(np.log(duration/target_duration)) > np.log(1.2):
                continue

            if number:
                # stop looking for episodes if we found enough already
                if len(episode_titles) > number:
                    break

            # skip track if adding it would not match first title duration
            if firstTitleContainsAll:
                if sum_duration + duration > firstDuration + 0.5 * target_duration:
                    break

            # if we passed all previous test,
            # then it is an episode
            episode = Episode(
                series=self.name,
                season=self.season,
                episode=self.first + len(episode_titles)
            )
            episode_titles[episode] = title
            sum_duration = sum_duration + title.duration

        return episode_titles

    def iter_episodes(self):

        episode_titles = self.find_episode_titles(duration=None, number=None)
        for episode in sorted(episode_titles):
            title = episode_titles[episode]
            yield episode, title


class TVSeriesDVDSet(object):
    """

    Parameters
    ----------
    name : str
        Name of the TV series
    season : int
        Season number of DVD set
    dvds : list
        Disc-ordered paths to dumped DVD directories
        (with "vobcopy -m -o `dvd`")
    lsdvd : str, optional
        Path to `lsdvd` command line tool (default to "lsdvd")
    """

    def __init__(self, name, season, dvds, lsdvd=None):

        super(TVSeriesDVDSet, self).__init__()
        self.name = name
        self.season = season
        self.dvds = []

        first = 1
        for dvd in dvds:
            tvSeriesDVD = TVSeriesDVD(
                name, season, first, dvd=dvd, lsdvd=lsdvd)
            self.dvds.append(tvSeriesDVD)
            first = first + len(tvSeriesDVD.find_episode_titles())

    def iter_episodes(self):

        for dvd in self.dvds:
            for episode, title in dvd.iter_episodes():
                yield episode, dvd, title
