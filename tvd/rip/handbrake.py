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


class HandBrakeCLI(CommandWrapper):
    """Rip previously dumped DVD.

    Parameters
    ----------
    handbrake : str, optional.
        Absolute path to `HandBrakeCLI` in case it is not reachable from PATH.

    """

    def __init__(self, handbrake=None):

        if handbrake is None:
            handbrake = 'HandBrakeCLI'

        super(HandBrakeCLI, self).__init__(handbrake)

    def extract_title(
        self, vobcopy_to, title, to,
        quality=18, rate=25,
        audio=None,
        subtitles=None
    ):
        """
        Rip DVD title into .mkv (with selected audio and subtitles tracks)

        Parameters
        ----------
        vobcopy_to : str
            Path to 'vobcopy' output
        title : int
            Title to rip
        to : str
            Path to HandBrake output
        quality : int
            Video quality. Ranges from 51 (low quality) to 0 (high quality).
            Defaults to 18. See https://trac.handbrake.fr/wiki/ConstantQuality
        rate : int
            Fixed frame rate. Defaults to 25.
        audio : list, optional
            Audio tracks with their names
            e.g. [(1, 'en'), (2, 'fr'), (3, 'es')]
        subtitles : list, optional
            Subtitle tracks
            e.g. [1, 2, 3, 4, 5, 6, 7, 8]

        """

        options = [
            '--input', vobcopy_to,
            '--title', str(title),
            '--output', to,
            '--format', 'mkv',
            '--encoder', 'x264',
            '--rate', str(rate),
            '--quality', str(quality),
        ]

        if audio is not None:

            # --audio 1,2,3
            audio_param = ','.join([str(stream) for stream, _ in audio])
            options.extend(['--audio', audio_param])

            # --audio copy,copy,copy
            aencoder_param = ','.join(['copy' for _, _ in audio])
            options.extend(['--aencoder', aencoder_param])

            # --aname en,fr,es
            aname_param = ','.join([name for _, name in audio])
            options.extend(['--aname', aname_param])

        if subtitles is not None:

            # --subtitle
            subtitles_param = ','.join([str(stream) for stream in subtitles])
            options.extend(['--subtitle', subtitles_param])

        self.run_command(options=options)
