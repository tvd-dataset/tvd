#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 CNRS (Hervé BREDIN - http://herve.niderb.fr/)
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


class PathMixin(object):

    def path_to_dump(self, disc, tvd_dir=None):

        pattern = (
            '{tvd}/{series}/dvd/dump/'
            'Season{season:02d}.Disc{disc:02d}'
        )

        if tvd_dir is None:
            raise ValueError('')

        return pattern.format(
            tvd=tvd_dir,
            series=self.__class__.__name__,
            disc=disc
        )

    def path_to_video(self, episode, tvd_dir=None):

        pattern = (
            '{tvd}/{series}/dvd/rip/video/'
            '{series}.Season{season:02d}.Episode{episode:02d}.mkv'
        )

        if tvd_dir is None:
            raise ValueError('')

        return pattern.format(
            tvd=tvd_dir,
            series=episode.series,
            season=episode.season,
            episode=episode.episode,
        )

    def path_to_audio(self, episode, language=None, tvd_dir=None):

        pattern = (
            '{tvd}/{series}/dvd/rip/audio/'
            '{series}.Season{season:02d}.Episode{episode:02d}.{language}.wav'
        )

        if tvd_dir is None:
            raise ValueError('')

        if language is None:
            language = self.language

        return pattern.format(
            tvd=tvd_dir,
            series=episode.series,
            season=episode.season,
            episode=episode.episode,
            language=language
        )

    def path_to_subtitles(self, episode, language=None, tvd_dir=None):

        pattern = (
            '{tvd}/{series}/dvd/rip/subtitles/'
            '{series}.Season{season:02d}.Episode{episode:02d}.{language}.srt'
        )

        if tvd_dir is None:
            raise ValueError('')

        if language is None:
            language = self.language

        return pattern.format(
            tvd=tvd_dir,
            series=episode.series,
            season=episode.season,
            episode=episode.episode,
            language=language
        )

    def path_to_stream(self, episode, format='mp4', tvd_dir=None):
        """
        Parameters
        ----------
        format : {'mp4', 'ogv', 'webm'}
            Defaults to 'mp4'
        """

        assert format in ['mp4', 'ogv', 'webm']
        assert tvd_dir is not None

        pattern = (
            '{tvd}/{series}/dvd/rip/stream/'
            '{series}.Season{season:02d}.Episode{episode:02d}.{format}'
        )

        if tvd_dir is None:
            raise ValueError('')

        return pattern.format(
            tvd=tvd_dir,
            series=episode.series,
            season=episode.season,
            episode=episode.episode,
            format=format
        )
