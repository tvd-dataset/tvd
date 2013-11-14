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
from lxml import objectify


class DVD(object):
    """

    Parameters
    ----------
    dvd : str, optional
        Path to dumped DVD directory (with "vobcopy -m -o `dvd`").
        Default uses physical DVD.
    lsdvd : str, optional
        Path to `lsdvd` command line tool (default to "lsdvd")
    xml : str or file, optional
        Use XML file precomputed by `lsdvd -Ox -avs`.
        When provided, both `dvd` and `lsdvd` parameters have no effect.
    """

    def __init__(self, dvd=None, lsdvd=None, xml=None):

        super(DVD, self).__init__()

        # path to `lsdvd` command line tool
        if lsdvd is None:
            lsdvd = 'lsdvd'

        # by default `lsdvd` will look for physical DVD
        self.dvd = '' if dvd is None else dvd

        if xml is None:

            # use lsdvd command line tool to extract DVD structure
            # TODO: error handle
            with open(os.devnull, mode='w') as f:
                xml_content = subprocess.check_output(
                    [lsdvd, '-Ox', '-avs', self.dvd], stderr=f
                )

        elif isinstance(xml, file):

            xml_content = xml.read()

        elif isinstance(xml, str):

            with open(xml, mode='r') as f:
                xml_content = f.read()

        # get rid of potentially buggy characters
        # TODO: find a better fix
        xml_content = xml_content.replace('\xff', '?').replace('&', '')

        # titles sorted in index order
        self.titles = sorted(
            [DVDTitle(t) for t in objectify.fromstring(xml_content).track[:]],
            key=lambda title: title.index,
        )

    # def __str__(self):
    #     import pandas
    #     LENGTH = 'DURATION'
    #     AUDIO = 'AUDIO TRACKS'
    #     SUBTITLE = 'SUBTITLE TRACKS'
    #     df = pandas.DataFrame(
    #         index=[t.index for t in self.titles],
    #         columns=[LENGTH, AUDIO, SUBTITLE]
    #     )

    #     for title in self.titles:
    #         df.ix[title.index, LENGTH] = title.duration / 60.
    #         df.ix[title.index, AUDIO] = ' '.join([a.langcode for a in title.audios])
    #         df.ix[title.index, SUBTITLE] = ' '.join([s.langcode for s in title.subtitles])

    #     return str(df)


class DVDTitle(object):

    def __init__(self, track):
        super(DVDTitle, self).__init__()
        self.index = int(track.ix)
        self.duration = float(track.length)
        if hasattr(track, 'audio'):
            self.audios = [
                DVDAudio(a) for a in track.audio[:]
            ]
        else:
            self.audios = []
        if hasattr(track, 'subp'):
            self.subtitles = [
                DVDSubtitle(s) for s in track.subp[:]
            ]
        else:
            self.subtitles = []

    def __str__(self):
        return "<DVDTitle dvd://%d>" % self.index

    def __repr__(self):
        return "<DVDTitle dvd://%d>" % self.index


class DVDAudio(object):

    def __init__(self, audio):
        super(DVDAudio, self).__init__()
        self.index = int(audio.ix)
        self.language = str(audio.language)
        self.langcode = str(audio.langcode)
        self.frequency = int(audio.frequency)
        self.channel = int(audio.channels)
        self.format = str(audio.format)


class DVDSubtitle(object):

    def __init__(self, subp):
        super(DVDSubtitle, self).__init__()
        self.index = int(subp.ix)
        self.language = str(subp.language)
        self.langcode = str(subp.langcode)
