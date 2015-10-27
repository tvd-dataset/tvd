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

# Vobcopy 1.2.0 - GPL Copyright (c) 2001 - 2009 robos@muon.de
#
# Usage: vobcopy
# if you want the main feature (title with most chapters)
# you don't need _any_ options!
# Options:
# [-m (mirror the whole dvd)]
# [-M (Main title - i.e. the longest (playing time) title on the dvd)]
# [-i /path/to/the/mounted/dvd/]
# [-n title-number]
# [-t <your name for the dvd>]
# [-o /path/to/output-dir/ (can be "stdout" or "-")]
# [-f (force output)]
# [-V (version)]
# [-v (verbose)]
# [-v -v (create log-file)]
# [-h (this here ;-)]
# [-I (infos about title, chapters and angles on the dvd)]
# [-1 /path/to/second/output/dir/] [-2 /.../third/..] [-3 /../] [-4 /../]
# [-b <skip-size-at-beginning[bkmg]>]
# [-e <skip-size-at-end[bkmg]>]
# [-O <single_file_name1,single_file_name2, ...>]
# [-q (quiet)]
# [-w <watchdog-minutes>]
# [-x (overwrite all)]
# [-F <fast-factor:1..64>]
# [-l (large-file support for files > 2GB)]

from __future__ import unicode_literals

from .command import CommandWrapper


class Vobcopy(CommandWrapper):
    """Dump DVD to disk.

    Parameters
    ----------
    vobcopy : str, optional.
        Absolute path to `vobcopy` in case it is not reachable from PATH.

    """

    def __init__(self, vobcopy=None):

        if vobcopy is None:
            vobcopy = 'vobcopy'

        super(Vobcopy, self).__init__(vobcopy, exists_params=['-h'])

    def __call__(self, to, name=None, dvd=None):
        """Dump DVD to disk

        Parameters
        ----------
        to : str
            Path to output directory
        dvd : str, optional
            Path to the mounted DVD

        """

        options = [
            '-q',      # quiet
            '-m',      # mirror the whole dvd
            '-o', to   # path to output directory
        ]

        if name:
            options.extend(['-t', name])  # DVD name

        if dvd:
            options.extend(['-i', dvd])   # /path/to/the/mounted/dvd

        self.run_command(options=options)
