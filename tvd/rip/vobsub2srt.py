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

from .command import CommandWrapper


class VobSub2SRT(CommandWrapper):
    """

    Parameters
    ----------
    vobsub2srt : str, optional.
        Absolute path to `vobsub2srt` in case it is not reachable from PATH.
    tessdata : str, optional
        Path to the "tessdata" directory.
    """

    def __init__(self, vobsub2srt=None, tessdata=None):

        if vobsub2srt is None:
            vobsub2srt = 'vobsub2srt'

        super(VobSub2SRT, self).__init__(vobsub2srt)
        self.tessdata = tessdata

    def __call__(self, mencoder_to, language):
        """Dump vobsub to disk

        Parameters
        ----------
        mencoder_to : str
            Path to output directory
        language : str
            Language code (e.g. "en", "fr", "es", "de")

        """

        options = [
            '--lang', language,
            '-vobsubout', mencoder_to,
            '--blacklist', '|'
        ]

        if self.tessdata is not None:
            options.extend(['--tesseract-data', self.tessdata])

        self.run_command(options=options)
