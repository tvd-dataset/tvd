#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 Hervé BREDIN (http://herve.niderb.fr/)
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

import numpy as np
from tvd.common.episode import Episode


class T(object):

    def __init__(self, episode=None):

        if episode is not None:
            assert isinstance(episode, Episode)
        self.episode = episode

    def __hash__(self):
        return hash(self.episode) + hash(self.T)

    def __eq__(self, other):
        return (self.episode == other.episode) and \
               (self.label == other.T)


class TAnchored(T):

    def __init__(self, seconds, episode=None):
        assert isinstance(seconds, np.float)
        super(TAnchored, self).__init__(episode=episode)
        self.T = seconds

    @property
    def is_anchored(self):
        return True

    @property
    def is_floating(self):
        return False



class TStart(TAnchored):
    """Episode start time"""
    def __init__(self, episode=None):
        super(TStart, self).__init__(-np.inf, episode=episode)


class TEnd(TAnchored):
    """Episode end time"""
    def __init__(self, episode=None):
        super(TStart, self).__init__(np.inf, episode=episode)


def _t():
    """Label generator

    Usage
    -----
    t = _t()
    next(t) -> 'A'    # start with 1-letter labels
    ...               # from A to Z
    next(t) -> 'Z'
    next(t) -> 'AA'   # then 2-letters labels
    next(t) -> 'AB'   # from AA to ZZ
    ...
    next(t) -> 'ZY'
    next(t) -> 'ZZ'
    next(t) -> 'AAA'  # then 3-letters labels
    ...               # (you get the idea)
    """

    import string
    import itertools

    # ABC...XYZ
    alphabet = string.uppercase

    # label lenght
    r = 1

    # infinite loop
    while True:

        # generate labels with current length
        for c in itertools.product(alphabet, repeat=r):
            yield "".join(c)

        # increment label length when all possibilities are exhausted
        r = r + 1


class TFloating(T):

    t = _t()

    @classmethod
    def reset(cls):
        """Reset label generator"""
        cls.t = _t()

    def __init__(self, episode=None):
        super(TFloating, self).__init__(episode=episode)
        self.T = next(self.__class__.t)

    @property
    def is_anchored(self):
        return False

    @property
    def is_floating(self):
        return True
