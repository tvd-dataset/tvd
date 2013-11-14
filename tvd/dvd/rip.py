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

import os
import subprocess


class DVDRip(object):

    def __init__(
        self,
        mplayer=None, mencoder=None,
        vobsub2srt=None, tessdata=None,
        sndfile_resample=None,
    ):
        super(DVDRip, self).__init__()

        self.mplayer = mplayer
        if mplayer is None:
            self.mplayer = 'mplayer'

        self.mencoder = mencoder
        if mencoder is None:
            self.mencoder = 'mencoder'

        self.vobsub2srt = vobsub2srt
        if vobsub2srt is None:
            self.vobsub2srt = 'vobsub2srt'

        self.env = dict(os.environ)
        if tessdata:
            self.env['TESSDATA_PREFIX'] = tessdata

        self.sndfile_resample = sndfile_resample
        if sndfile_resample is None:
            self.sndfile_resample = 'sndfile-resample'

    def dump_subtitles(self, dvd, title, srtWithLangcodePlaceholder):

        for s, subtitle in enumerate(title.subtitles):

            path = srtWithLangcodePlaceholder % subtitle.langcode

            # ======================
            # extract .sub and .idx
            # ======================

            cmd = [
                self.mencoder,
                'dvd://%d' % title.index,
                '-dvd-device' if dvd.dvd else '',
                '%s/VIDEO_TS' % dvd.dvd if dvd.dvd else '',
                '-o', '/dev/null',
                '-nosound',
                '-ovc', 'copy',
                '-vobsubout', path,
                '-slang', subtitle.langcode,
                '-ss', '0',
                '-endpos', str(title.duration),
            ]

            with open(os.devnull, mode='w') as f:
                subprocess.check_call(cmd, stderr=f, stdout=f, env=self.env)

            # ==========
            # apply OCR
            # ==========

            cmd = [
                self.vobsub2srt,
                '--lang', subtitle.langcode,
                '-vobsubout', path,
            ]

            with open(os.devnull, mode='w') as f:
                subprocess.check_call(cmd, stderr=f, stdout=f, env=self.env)

    def dump_audio(self, dvd, title, wavWithLangcodePlaceholder):
        """
            xxxx.{en|fr|es|...}.xxxx.wav

        Parameters
        ----------
        dvd : `tvd.DVD`
        title : `tvd.DVDTitle`
        wavWithLangcodePlaceholder : str
            e.g. /path/to/TheBigBangTheory.Season01.Episode01.%s


        """

        for a, audio in enumerate(title.audios):

            raw = wavWithLangcodePlaceholder % ('raw.' + audio.langcode) + '.wav'
            wav = wavWithLangcodePlaceholder % (audio.langcode) + '.wav'

            # =================
            # extract raw mono
            # =================

            cmd = [
                self.mplayer,
                'dvd://%d' % title.index,
                '-dvd-device' if dvd.dvd else '',
                '%s/VIDEO_TS' % dvd.dvd if dvd.dvd else '',
                '-vc', 'null',
                '-vo', 'null',
                '-alang', audio.langcode,
                '-ao', 'pcm:waveheader:file=%s' % raw,
                '-channels', '1',
                '-ss', '0',
                '-endpos', str(title.duration),
            ]

            with open(os.devnull, mode='w') as f:
                subprocess.check_call(cmd, stderr=f, stdout=f)

            # ==================
            # downsample to 16k
            # ==================

            cmd = [
                self.sndfile_resample,
                '-to', str(16000),
                '-c', str(1),
                raw, wav
            ]

            with open(os.devnull, mode='w') as f:
                subprocess.check_call(cmd, stderr=f, stdout=f)

    def dump_vob(self, dvd, title, vob):
        """

        `prefix`.vob
        `prefix`.mp4
        `prefix`.webm
        `prefix`.ogv


        Use mplayer to dump DVD title .vob

        Parameters
        ----------
        dvd : `tvd.DVD`
        title : `tvd.DVDTitle`
        vob : str

        """

        # ================
        # extract raw vob
        # ================

        cmd = [
            self.mplayer,
            '-dvd-device' if dvd.dvd else '',
            '%s/VIDEO_TS' % dvd.dvd if dvd.dvd else '',
            '-dumpstream', 'dvd://%d' % title.index,
            '-dumpfile', vob + '.vob',
        ]

        with open(os.devnull, mode='w') as f:
            subprocess.check_call(cmd, stderr=f, stdout=f, env=self.env)
