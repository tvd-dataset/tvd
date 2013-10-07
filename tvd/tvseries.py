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

from tvd.dvd import DVD
import numpy as np


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
                key=lambda (title, duration): duration,
                reverse=True,
            )
        )

        # estimate episode duration as
        # median of n+1 longest titles
        return np.median(durations[:number+1])

    def find_episodes(self, duration=None, number=None):
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
        episodes = []
        sum_duration = 0.

        for title in self.titles:

            # title duration
            duration = title.duration

            # skip title if its duration is not close enough to target duration
            if np.abs(np.log(duration/target_duration)) > np.log(1.2):
                continue

            if number:
                # stop looking for episodes if we found enough already
                if len(episodes) > number:
                    break

            # skip track if adding it would not match first title duration
            if firstTitleContainsAll:
                if sum_duration + duration > firstDuration + 0.5 * target_duration:
                    break

            # if we passed all previous test,
            # then it is an episode
            episodes.append(title)
            sum_duration = sum_duration + title.duration

        return episodes

    def dump(self, rip, path, verbose=True):

        episodes = self.find_episodes(duration=None, number=None)

        for e, episode in enumerate(episodes):

            print "%s.Season%02d.Episode%02d" % (
                self.name, self.season, self.first + e)

            prefix = '%s/%s.Season%02d.Episode%02d' % (
                path, self.name, self.season, self.first + e)

            print "  --> video"
            rip.dump_vob(self, episode, prefix)
            print "  --> audio tracks"
            rip.dump_audio(self, episode, prefix + '.%s')
            print "  --> subtitles"
            rip.dump_subtitles(self, episode, prefix + '.%s')
