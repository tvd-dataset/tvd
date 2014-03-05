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


import networkx as nx
import numpy as np

TVD_DESCRIPTION = 'description'
TVD_SPEAKER = 'speaker'
TVD_SPEECH = 'speech'


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


class T(object):
    """(floating) timestamps

    Parameters
    ----------
    seconds : float, optional
    """

    t = _t()

    @classmethod
    def reset(cls):
        """Reset label generator"""
        cls.t = _t()

    def __init__(self, seconds=None):

        if seconds is None:
            self.fixed = False
            self.label = next(self.__class__.t)

        else:
            self.fixed = True
            self.label = seconds

    def __hash__(self):
        return hash(self.label) + hash(self.fixed)

    def __eq__(self, other):
        return self.fixed == other.fixed and self.label == other.label

    def __str__(self):
        if self.fixed:
            return '%.3f' % self.label
        else:
            return self.label

    def set(self, seconds):
        """Anchor timestamps

        Parameters
        ----------
        seconds : float
        """
        self.fixed = True
        self.label = seconds


class AnnotationGraph(nx.MultiDiGraph):

    def __init__(self):
        super(AnnotationGraph, self).__init__()
        t_start = T(seconds=-np.inf)
        t_end = T(seconds=np.inf)
        self.add_node(t_start)
        self.add_node(t_end)

    def add_annotation(
        self,
        start_time, end_time,
        annotation_type, annotation_value
    ):
        """

        Parameters
        ----------
        start_time, end_time : `T`
        annotation_type : str
        annotation_value : hashable
        """

        self.add_edge(
            start_time, end_time,
            **{annotation_type: annotation_value}
        )

    def align(self, time1, time2):
        pass
