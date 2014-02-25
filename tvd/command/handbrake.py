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

        super(HandBrakeCLI, self).__init__(handbrake, exists_params=['-h'])

    def __call__(self, vobcopy_to, title, to, audio, subtitles):
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
        audio : list
            Audio tracks with their names
            e.g. [(1, 'en'), (2, 'fr'), (3, 'es')]
        subtitles : list
            Subtitle tracks
            e.g. [1, 2, 3, 4, 5, 6, 7, 8]

        """

        options = [
            '--input', vobcopy_to,  # --input TVD/TheBigBangTheory/dvd/dump/Season01.Disc01
            '--title', str(title),  # --title 2
            '--output', to,         # --output TheBigBangTheory/dvd/rid/TheBigBangTheory.Season01.Episode01.mkv
            '--format', 'mkv',      # --format mkv
            '--encoder', 'x264',    # --encoder x264
            '--rate', '25',         # --rate 25
            '--cfr'                 # --cfr
        ]

        # --audio 1,2,3
        audio_param = ','.join([str(stream) for stream, _ in audio])
        options.extend(['--audio', audio_param])

        # --audio copy,copy,copy
        aencoder_param = ','.join(['copy' for _, _ in audio])
        options.extend(['--aencoder', aencoder_param])

        # --aname en,fr,es
        aname_param = ','.join([name for _, name in audio])
        options.extend(['--aname', aname_param])

        # --subtitle
        subtitles_param = ','.join([str(stream) for stream in subtitles])
        options.extend(['--subtitle', subtitles_param])

        self.run_command(options=options)
