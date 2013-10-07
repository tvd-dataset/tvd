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

from tvd.tvseries import TVSeriesDVD
import numpy as np
import pandas

from pkg_resources import resource_filename


class test_TVSeriesDVD(object):

    def setup(self):

        # load DVD groundtruth
        self.dvds = pandas.read_csv(
            resource_filename(__package__, 'data/test.csv'),
            converters={
                'series': str,
                'season': int,
                'disc': int,
                'xml': str,
                'episodeDuration': lambda value: float(value)*60,
                'numberOfEpisodes': int,
                'titles': lambda value: [int(t) for t in value.split()]
            }
        )

    def teardown(self):
        pass

    def test_guessDuration(self):

        for _, row in self.dvds.iterrows():

            duration = row['episodeDuration']

            dvd = TVSeriesDVD(
                row['series'], row['season'], row['disc'],
                xml=resource_filename(__package__, 'data/%s' % row['xml'])
            )

            assert np.abs(
                np.log(dvd.guess_episode_duration()/duration)) < np.log(1.1)

    def test_guessDurationWithNumber(self):

        for _, row in self.dvds.iterrows():

            duration = row['episodeDuration']

            dvd = TVSeriesDVD(
                row['series'], row['season'], row['disc'],
                xml=resource_filename(__package__, 'data/%s' % row['xml'])
            )

            assert np.abs(
                np.log(
                    dvd.guess_episode_duration(
                        number=row['numberOfEpisodes'])/duration
                    )
                ) < np.log(1.1)

    def test_findEpisodes(self):

        for _, row in self.dvds.iterrows():

            titles = row['titles']

            dvd = TVSeriesDVD(
                row['series'], row['season'], row['disc'],
                xml=resource_filename(__package__, 'data/%s' % row['xml'])
            )

            episodes = dvd.find_episodes()

            assert titles == [e.index for e in episodes]

    def test_findEpisodesWithNumber(self):

        for _, row in self.dvds.iterrows():

            titles = row['titles']

            dvd = TVSeriesDVD(
                row['series'], row['season'], row['disc'],
                xml=resource_filename(__package__, 'data/%s' % row['xml'])
            )

            episodes = dvd.find_episodes(number=row['numberOfEpisodes'])

            assert titles == [e.index for e in episodes]

    def test_findEpisodesWithDuration(self):

        for _, row in self.dvds.iterrows():

            titles = row['titles']

            dvd = TVSeriesDVD(
                row['series'], row['season'], row['disc'],
                xml=resource_filename(__package__, 'data/%s' % row['xml'])
            )

            episodes = dvd.find_episodes(duration=row['episodeDuration'])

            assert titles == [e.index for e in episodes]

    def test_findEpisodesWithDurationAndNumber(self):

        for _, row in self.dvds.iterrows():

            titles = row['titles']

            dvd = TVSeriesDVD(
                row['series'], row['season'], row['disc'],
                xml=resource_filename(__package__, 'data/%s' % row['xml'])
            )

            episodes = dvd.find_episodes(
                number=row['numberOfEpisodes'],
                duration=row['episodeDuration']
            )

            assert titles == [e.index for e in episodes]
