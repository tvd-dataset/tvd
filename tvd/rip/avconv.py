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


class AVConv(CommandWrapper):
    """Convert audio or video streams

    Parameters
    ----------
    avconv : str, optional.
        Absolute path to `avconv` in case it is not reachable from PATH.

    """

    def __init__(self, avconv=None):

        if avconv is None:
            avconv = 'avconv'

        super(AVConv, self).__init__(avconv)

    def audio_track(self, handbrake_to, stream, to):
        """
        Extract audio track from HandBrake output

        Parameters
        ----------
        handbrake_to : str
            Path to input file
        stream : int
        to : str
            Path to output file

        See savvyadmin.com/extract-audio-from-video-files-to-wav-using-ffmpeg

        """

        options = [
            '-y',
            '-i', handbrake_to,
            '-map', '0:{stream:d}'.format(stream=stream),
            '-acodec', 'pcm_s16le',
            '-ac', '1',
            to
        ]

        self.run_command(options=options, env=None)

    # http://www.willus.com/author/streaming2.shtml
    # -map option details can be foundhere :
    # http://libav.org/avconv.html#Advanced-options

    def mp4(self, handbrake_to, audio_stream, to):

        options = [
            '-y',
            '-i', handbrake_to,
            '-map', '0:0,0:0',
            '-i_qfactor', '0.71',
            '-qcomp', '0.6',
            '-qmin', '10',
            '-qmax', '63',
            '-qdiff', '4',
            '-trellis', '0',
            '-vcodec', 'libx264',
            '-b:v', '200k',
            '-map', '0:{stream:d},0:0'.format(stream=audio_stream),
            '-b:a', '56k',
            '-ar', '22050',
            '-ac', '2',
            '-acodec', 'libvo_aacenc',
            to
        ]

        self.run_command(options=options, env=None)

    def webm(self, handbrake_to, audio_stream, to):

        options = [
            '-y',
            '-i', handbrake_to,
            '-map', '0:0,0:0',
            '-qmax', '63',
            '-b:v', '200k',
            '-vcodec', 'libvpx',
            '-map', '0:{stream:d},0:0'.format(stream=audio_stream),
            '-b:a', '56k',
            '-ar', '22050',
            '-ac', '2',
            '-acodec', 'libvorbis',
            to
        ]

        self.run_command(options=options, env=None)

    def ogv(self, handbrake_to, audio_stream, to):

        options = [
            '-y',
            '-i', handbrake_to,
            '-map', '0:0,0:0',
            '-qmax', '63',
            '-b:v', '200k',
            '-vcodec', 'libtheora',
            '-map', '0:{stream:d},0:0'.format(stream=audio_stream),
            '-b:a', '56k',
            '-ar', '22050',
            '-ac', '2',
            '-acodec', 'libvorbis',
            to
        ]

        self.run_command(options=options, env=None)
