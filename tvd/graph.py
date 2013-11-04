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


def _t():

    import string
    import itertools

    alphabet = string.uppercase

    r = 1
    while True:
        for c in itertools.product(alphabet, repeat=r):
            yield "".join(c)
        r = r + 1


class T(object):

    t = _t()

    @classmethod
    def reset(cls):
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
        self.fixed = True
        self.label = seconds

