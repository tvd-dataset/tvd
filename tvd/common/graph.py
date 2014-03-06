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

import networkx as nx
from tvd.common.time import TFloating, TAnchored, TStart, TEnd


class AnnotationGraph(nx.MultiDiGraph):
    """

    >>> from tvd import Episode, T
    >>> G = AnnotationGraph()
    >>> episode = Episode(series="GameOfThrones", season=1, episode=1)
    >>> t1 = T(episode=episode)
    >>> t2 = T(episode=episode)
    >>> G.add_edge(t1, t2, attr_dict={'speaker': 'John', 'speech': 'Hello'})

    """

    def __init__(self, episode=None):
        super(AnnotationGraph, self).__init__()

        # initialize the graph with episode start & end
        self.add_node(TStart(episode=episode))
        self.add_node(TEnd(episode=episode))

    def add_annotation(self, t1, t2, data):
        """Add annotation to the graph between instants t1 and t2

        Parameters
        ----------
        t1, t2: `tvd.TFloating` or `tvd.TAnchored`
        data : dict
            {annotation_type: annotation_value} dictionary

        Example
        -------
        >>> G = AnnotationGraph()
        >>> t1 = TAnchored(1.000)
        >>> t2 = TFloating()
        >>> data = {'speaker': 'John', 'speech': 'Hello world!'}
        >>> G.add_annotation(t1, t2, data)
        """

        # make sure those are T instances
        assert isinstance(t1, (TFloating, TAnchored))
        assert isinstance(t2, (TFloating, TAnchored))

        # make sure Ts are connected in correct chronological order
        if t1.is_anchored and t2.is_anchored:
            assert t1.T <= t2.T

        self.add_edge(t1, t2, attr_dict=data)

    def anchor(self, floating_t, anchored_t):
        """Anchor `floating_t`

        Parameters
        ----------
        floating_t : TFloating
            Floating time to anchor
        anchored_t : TAnchored
            When to anchor `floating_t`

        """
        assert (floating_t in self) and (not floating_t.is_anchored)
        assert isinstance(anchored_t, TAnchored)

        # add a (t --> anchored_t) edge for each (t --> floating_t) edge
        for t, _, key, data in self.in_edges_iter(
            nbunch=[floating_t], data=True, keys=True
        ):
            self.add_edge(t, anchored_t, key=key, attr_dict=data)

        # add a (anchored_t --> t) edge for each (floating_t --> t) edge
        for _, t, key, data in self.edges_iter(
            nbunch=[floating_t], data=True, keys=True
        ):
            self.add_edge(anchored_t, t, key=key, attr_dict=data)

        # remove floating_t node (as it was replaced by anchored_t)
        self.remove_node(floating_t)

    def align(self, floating_t, other_t):
        assert not floating_t.fixed
        self.anchor(floating_t, other_t)
