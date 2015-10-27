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
from collections import namedtuple
from pyannote.core.json import PYANNOTE_JSON_CONTENT
from .json import TVD_JSON


class Episode(namedtuple('Episode', ['series', 'season', 'episode'])):
    """
    Parameters
    ----------
    series : str
    season : int
    episode : int
    """

    def __new__(cls, series, season, episode):
        return super(Episode, cls).__new__(cls, series, season, episode)

    def __str__(self):
        return '%s.Season%02d.Episode%02d' % (
            self.series, self.season, self.episode)

    def for_json(self):
        data = {TVD_JSON: self.__class__.__name__}
        data[PYANNOTE_JSON_CONTENT] = {'series': self.series,
                                       'season': self.season,
                                       'episode': self.episode}
        return data

    @classmethod
    def from_json(cls, data):
        series = data[PYANNOTE_JSON_CONTENT]['series']
        season = data[PYANNOTE_JSON_CONTENT]['season']
        episode = data[PYANNOTE_JSON_CONTENT]['episode']
        return cls(series=series, season=season, episode=episode)
