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
               (self.T == other.T)

    def __lt__(self, other):
        if self.episode == other.episode:
            return self.T < other.T
        else:
            return self.episode < other.episode

    def for_json(self):
        """
        Usage
        -----
        >>> import simplejson as json
        >>> t = TFloating()
        >>> json.dumps(t, for_json=True)
        """

        d = {'__T__': self.T}
        if self.episode:
            d['episode'] = self.episode
        return d

    @classmethod
    def from_json(cls, d):
        """
        Usage
        -----
        >>> import simplejson as json
        >>> from tvd.common.io import object_hook
        >>> with open('time.json', 'r') as f:
        ...   t = json.load(f, object_hook=object_hook)
        """

        t = d['__T__']

        episode = None
        if 'episode' in d:
            episode = d['episode']

        if isinstance(t, str):
            return TFloating(label=t, episode=episode)

        if t == float('-inf'):
            return TStart(episode=episode)

        if t == float('inf'):
            return TEnd(episode=episode)

        return TAnchored(t, episode=episode)


class TAnchored(T):
    """Anchored time

    Parameters
    ----------
    seconds : float
        Seconds since beginning
    episode : `tvd.Episode`, optional
        Episode (in case the graph contains multiple episodes)
    """

    def __init__(self, seconds, episode=None):
        super(TAnchored, self).__init__(episode=episode)
        self.T = np.float(seconds)

    @property
    def is_anchored(self):
        return True

    @property
    def is_floating(self):
        return False

    def __repr__(self):
        return '<{time:.3f}{sep}{episode}>'.format(
            time=self.T,
            sep="" if not self.episode else "|",
            episode="" if not self.episode else self.episode
        )


class TStart(TAnchored):
    """Episode start"""

    def __init__(self, episode=None):
        super(TStart, self).__init__(-np.inf, episode=episode)

    def __repr__(self):
        return '<start{sep}{episode}>'.format(
            sep="" if not self.episode else "|",
            episode="" if not self.episode else self.episode
        )


class TEnd(TAnchored):
    """Episode end"""

    def __init__(self, episode=None):
        super(TEnd, self).__init__(np.inf, episode=episode)

    def __repr__(self):
        return '<end{sep}{episode}>'.format(
            sep="" if not self.episode else "|",
            episode="" if not self.episode else self.episode
        )


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
    """Floating time

    Parameters
    ----------
    label : str, optional
        Floating time unique identifier.
        When not provided, a unique identifier is automatically generated
        for each new instance of `TFloating` (A, B, ..., Z, AA, AB, ...)
        TFloating.reset() can be used to reset label generator to A.
    episode : `tvd.Episode`, optional
    """

    t = _t()

    @classmethod
    def reset(cls):
        """Reset label generator"""
        cls.t = _t()

    def __init__(self, label=None, episode=None):
        super(TFloating, self).__init__(episode=episode)
        if label is None:
            self.T = next(self.__class__.t)
        else:
            assert isinstance(label, str)
            self.T = label

    @property
    def is_anchored(self):
        return False

    @property
    def is_floating(self):
        return True

    def __repr__(self):
        return '<{label:s}{sep}{episode}>'.format(
            label=self.T,
            sep="" if not self.episode else "|",
            episode="" if not self.episode else self.episode
        )
