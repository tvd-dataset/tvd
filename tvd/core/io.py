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


from tvd.core.time import T
from tvd.core.graph import AnnotationGraph
from tvd.core.episode import Episode


def object_hook(d):
    """
    Usage
    -----
    >>> import simplejson as json
    >>> with open('file.json', 'r') as f:
    ...   json.load(f, object_hook=object_hook)
    """

    if '__E__' in d:
        return Episode._from_json(d)

    if '__T__' in d:
        return T._from_json(d)

    if '__G__' in d:
        return AnnotationGraph._from_json(d)

    return d


def mapping_error_handler(unicode_error):
    mapping = {
        u"’": u"'",
        u"…": u"...",
        u"–": u"-",
        u"—": u"-",
        u" ": u" ",
        u"‘": u"'",
        u"ê": u"e",
        u"  ": u" ",
        u"é": u"e",
        u"“": u'"',
        u"”": u'"',
    }
    character = unicode_error.object[unicode_error.start:unicode_error.end]
    if character not in mapping:
        logging.info('Removed character [%s]' % character)
    return (mapping.get(character, ''), unicode_error.end)
