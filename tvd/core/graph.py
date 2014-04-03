#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 CNRS (Hervé BREDIN -- http://herve.niderb.fr/)
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
from networkx.readwrite.json_graph import node_link_data, node_link_graph

from tvd.core.time import TFloating, TAnchored

import simplejson as json
import itertools


class AnnotationGraph(nx.MultiDiGraph):
    """Annotation graph

    Parameters
    ----------
    episode : `tvd.Episode`
        Episode (in case the graph contains only one episode)

    Example
    -------
    >>> from tvd import Episode, TFloating, TAnchored
    >>> G = AnnotationGraph()
    >>> episode = Episode(series="GameOfThrones", season=1, episode=1)
    >>> t1 = TAnchored(10.3, episode=episode)
    >>> t2 = TFloating(episode=episode)
    >>> G.add_annotation(
            t1, t2,
            {'speaker': 'John', 'speech': 'Hello'}
        )

    """

    def __init__(self, graph=None, episode=None):
        super(AnnotationGraph, self).__init__(data=graph, episode=episode)

    def floating(self):
        """Get list of floating times"""
        return [n for n in self if n.is_floating]

    def anchored(self):
        """Get list of anchored times"""
        return [n for n in self if n.is_anchored]

    def add_annotation(self, t1, t2, data=None):
        """Add annotation to the graph between times t1 and t2

        Parameters
        ----------
        t1, t2: `tvd.TFloating` or `tvd.TAnchored`
        data : dict, optional
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

    def _merge(self, floating_t, another_t):
        """Helper function to merge `floating_t` with `another_t`

        Assumes that both `floating_t` and `another_t` exists.
        Also assumes that `floating_t` is an instance of `TFloating`
        (otherwise, this might lead to weird graph configuration)

        Parameters
        ----------
        floating_t : `TFloating`
            Existing floating time in graph
        another_t : `TAnchored` or `TFloating`
            Existing time in graph
        """
        # floating_t and another_t must exist in graph

        # add a (t --> another_t) edge for each (t --> floating_t) edge
        for t, _, key, data in self.in_edges_iter(
            nbunch=[floating_t], data=True, keys=True
        ):
            self.add_edge(t, another_t, key=key, attr_dict=data)

        # add a (another_t --> t) edge for each (floating_t --> t) edge
        for _, t, key, data in self.edges_iter(
            nbunch=[floating_t], data=True, keys=True
        ):
            self.add_edge(another_t, t, key=key, attr_dict=data)

        # remove floating_t node (as it was replaced by another_t)
        self.remove_node(floating_t)

    def anchor(self, floating_t, anchored_t):
        """Anchor `floating_t` at `anchored_t`

        Parameters
        ----------
        floating_t : TFloating
            Floating time to anchor
        anchored_t : TAnchored
            When to anchor `floating_t`

        """
        assert (floating_t in self) and (not floating_t.is_anchored)
        assert isinstance(anchored_t, TAnchored)

        if anchored_t not in self:
            self.add_node(anchored_t)

        self._merge(floating_t, anchored_t)

    def align(self, one_t, another_t):
        """Align two (potentially floating) times

        `one_t` and `another_t` cannot both be anchored at the same time
        In case `another_t` is anchored, this is similar to `anchor` method

        Parameters
        ----------
        one_t, another_t : `TFloating` or `TAnchored`
            Two times to be aligned.
        """

        assert one_t in self
        assert another_t in self

        # first time is floating
        if one_t.isfloating:
            self._merge(one_t, another_t)

        # second time is floating
        elif another_t.isfloating:
            self._merge(another_t, one_t)

        # both times are anchored --> FAIL
        else:
            raise ValueError(
                'Cannot align two anchored times')

    # =========================================================================

    def ordering_graph(self):
        """Ordering graph

        t1 --> t2 in the ordering graph indicates that t1 happens before t2.
        A missing edge simply means that it is not clear yet.

        >>> from tvd import AnnotationGraph, TStart, TEnd, TAnchored, TFloating
        >>> g = AnnotationGraph()
        >>> t1 = TAnchored(10)
        >>> t2 = TAnchored(20)
        >>> a = TFloating()
        >>> b = TFloating()
        >>> c = TFloating()
        >>> g.add_annotation(t1, a)
        >>> g.add_annotation(a, t2)
        >>> g.add_annotation(t1, b)
        >>> g.add_annotation(b, c)
        >>> g.add_annotation(c, t2)
        """

        g = nx.DiGraph()

        # add times
        for t in self.nodes_iter():
            g.add_node(t)

        # add existing edges
        for t1, t2 in self.edges_iter():
            g.add_edge(t1, t2)

        # connect every pair of anchored times
        anchored = sorted(self.anchored())
        for t1, t2 in itertools.combinations(anchored, 2):
            g.add_edge(t1, t2)

        # connect every time with its sucessors
        _g = g.copy()
        for t1 in _g:
            for t2 in set([target for (_, target) in nx.bfs_edges(_g, t1)]):
                g.add_edge(t1, t2)

        return g

    def ordered_edges_iter(self, data=False, keys=False):
        """Return an iterator over the edges in temporal/topological order.

        Ordered edges are returned as tuples with optional data and keys
        in the order (t1, t2, key, data).

        Parameters
        ----------
        data : bool, optional (default=False)
            If True, return edge attribute dict with each edge.
        keys : bool, optional (default=False)
            If True, return edge keys with each edge.

        Returns
        -------
        edge_iter : iterator
            An iterator of (u,v), (u,v,d) or (u,v,key,d) tuples of edges.
        """

        # start by sorting nodes in temporal+topological order
        o = self.ordering_graph()
        nodes = nx.topological_sort(o)

        # iterate over edges using this very order
        for _ in self.edges_iter(nbunch=nodes, data=data, keys=keys):
            yield _

    # =========================================================================

    def _anchored_successors(self, n):
        """Get all first anchored successors"""

        # loop on all outgoing edges
        for t in self.successors(n):
            
            # if neighbor is anchored
            # stop looking for (necessarily later) successors
            if t.is_anchored:
                yield t
                continue

            # if neighbor is not anchored
            # look one level deeper
            for tt in self._anchored_successors(t):
                yield tt

    def _anchored_predecessors(self, n):
        """Get all first anchored predecessors"""

        # loop on all incoming edges
        for t in self.predecessors(n):
            
            # if predecessor is anchored
            # stop looking for (necessarily earlier) predecessors
            if t.is_anchored:
                yield t
                continue
            
            # if neighbor is not anchored
            # look one level deeper
            for tt in self._anchored_predecessors(t):
                yield tt

    def timerange(self, t):
        """Infer smallest possible timerange from graph structure

        Returns
        -------
        (left, right) tuple
            left == None or right == None indicates that the current state of
            the annotation graph does not allow to decide the boundary.

        """

        if isinstance(t, TAnchored):
            return (t.T, t.T)
        successors = [n for n in self._anchored_successors(t)]
        predecessors = [n for n in self._anchored_predecessors(t)]

        earlier_successor = None
        if successors:
            earlier_successor = min(successors)

        later_predecessor = None
        if predecessors:
            later_predecessor = max(predecessors)

        return (later_predecessor.T, earlier_successor.T)

    # =========================================================================

    def for_json(self):
        """
        Usage
        -----
        >>> import simplejson as json
        >>> g = AnnotationGraph()
        >>> json.dumps(g, for_json=True)
        """
        data = node_link_data(self)
        data['__G__'] = True
        return data

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self, f, for_json=True)

    # -------------------------------------------------------------------------

    @classmethod
    def _from_json(cls, d):
        """
        Usage
        -----
        >>> import simplejson as json
        >>> from tvd.core.io import object_hook
        >>> with open('graph.json', 'r') as f:
        ...   g = json.load(f, object_hook=object_hook)
        """
        g = node_link_graph(d)
        return cls(graph=g, episode=g.graph['episode'])

    @classmethod
    def load(cls, path):
        from tvd.core.io import object_hook
        with open(path, 'r') as f:
            g = json.load(f, object_hook=object_hook)
        return g

