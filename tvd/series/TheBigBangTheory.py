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

from tvd.www.www import WebResources


class TheBigBangTheory(WebResources):

    def __init__(self):
        super(TheBigBangTheory, self).__init__(series=self.__class__.__name__)

    def outline(self, url, source=None, episode=None):
        """
        Parameters
        ----------
        url : str
            URL where resource is available
        source : str, optional
            Textual description of the source of the resource
        episode : Episode, optional
            Episode for which resource should be downloaded
            Useful in case a same URL contains resources for multiple episodes.

        Returns
        -------
        g : AnnotationGraph
        """
        # should return an annotation graph
        pass

    def manual_transcript(self, url, source=None, episode=None):

        # should return an annotation graph
        pass
