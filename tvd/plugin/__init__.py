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

from __future__ import unicode_literals

import logging
import wave
import contextlib
import yaml
from pkg_resources import resource_filename

from ..core import Episode
from resource import ResourceMixin
from path import PathMixin
from rip import RipMixin

CONFIG_HUMAN_READABLE_NAME = 'name'
CONFIG_ORIGINAL_LANGUAGE = 'language'
CONFIG_EPISODES = 'episodes'
CONFIG_RESOURCES = 'resources'


class Plugin(ResourceMixin, PathMixin, RipMixin):

    def __init__(self, root):
        super(Plugin, self).__init__()

        self.tvd_dir = root

        # obtain path to YAML configuration file and load it
        path = resource_filename(self.__class__.__name__, 'tvd.yml')
        with open(path, mode='r') as f:
            self.config = yaml.load(f)

        # human readable name is obtained from YAML configuration file
        self.name = self.config[CONFIG_HUMAN_READABLE_NAME]

        # original language is obtained from YAML configuration file
        self.language = self.config[CONFIG_ORIGINAL_LANGUAGE]

        # list of episodes according to configuration file
        # e.g. episodes: [17, 23, 23] ==> season 1 (2, 3) with 17 (23, 23) eps
        episodes = self.config.get(CONFIG_EPISODES, [])
        self.episodes = [
            Episode(
                series=self.__class__.__name__,
                season=season_index+1,
                episode=episode_index+1
            )
            for season_index, n_episodes in enumerate(episodes)
            for episode_index in range(n_episodes)
        ]

        # load 'resources' section from YAML configuration file
        resources = self.config.get(CONFIG_RESOURCES, {})
        self.init_resource(resources)

    def get_episode_duration(self, episode):
        """Get episode duration from .wav file

        Parameters
        ----------
        episode : Episode

        """

        wav = self.path_to_audio(episode, language=self.language)
        # TODO -- check if wav file exists

        with contextlib.closing(wave.open(wav, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()

        duration = frames / float(rate)
        return duration
