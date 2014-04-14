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
import logging

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


MAPPING = {
    u'\u2013': u"-",    # –
    u'\u2018': u"'",    # ‘
    u'\u2019': u"'",    # ’
    u'\u2026': u"...",  # …
    u'\u201c': u'"',    # “
    u'\u201d': u'"',    # ”
    u'\u200b': u" ",     #    
    u'\u2014': u"-",    # —
}

def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate

# encoding error handler
@static_var('mapping', MAPPING)
def handler(error):
    character = error.object[error.start:error.end]
    if character not in handler.mapping:
        handler.mapping[character] = u''
        logging.warn(
            u"Unmapped character %s %s" % (repr(character), character))
    return (handler.mapping[character], error.end)
