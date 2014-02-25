#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2014 Hervé BREDIN (http://herve.niderb.fr/)
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

from tvd.command.command import CommandWrapper


class MEncoder(CommandWrapper):
    """Rip previously dumped DVD.

    Parameters
    ----------
    mencoder : str, optional.
        Absolute path to `mencoder` in case it is not reachable from PATH.

    """

    def __init__(self, mencoder=None):

        if mencoder is None:
            mencoder = 'mencoder'

        super(MEncoder, self).__init__(mencoder)

    def vobsub(self, vobcopy_to, title, language, to):
        """
        Extract vobsub from DVD title

        Parameters
        ----------
        vobcopy_to : str
            Path to 'vobcopy' output
        title : int
            Title to process
        language : str
            Language code (e.g. "en", "fr", "es", "de")
        to : str
            Path to output (without extension)
        """

        options = [
            'dvd://{title:d}'.format(title=title),
            '-dvd-device', vobcopy_to,  # TVD/TheBigBangTheory/dvd/dump/Season01.Disc01
            '-o', '/dev/null',
            '-nosound',
            '-ovc', 'copy',
            '-vobsubout', to,
            '-slang', language,
        ]

        self.run_command(options=options)
