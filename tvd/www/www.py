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

import yaml
import logging
from pkg_resources import resource_filename

from tvd.common.episode import Episode

NAME = 'name'
LANGUAGE = 'language'
WWW = 'www'
SOURCE = 'source'
URL = 'url'
SEASON = 'season'
EPISODE = 'episode'


class WebResources(object):

    def __init__(self, series=None):

        super(WebResources, self).__init__()

        path = resource_filename('tvd.series', '%s.yml' % series)
        with open(path, mode='r') as f:
            config = yaml.load(f)

        self.series = series
        self.name = config[NAME]
        self.language = config[LANGUAGE]

        self.resource_url = {}
        self.resource_src = {}

        www = config[WWW]
        for resourceType in www:

            self.resource_src[resourceType] = www.get(SOURCE, None)

            self.resource_url[resourceType] = {}
            for url in www[resourceType][URL]:

                season_number = url.get(SEASON, None)
                episode_number = url.get(EPISODE, None)
                if season_number is None or episode_number is None:
                    raise ValueError(
                        'Missing season or episode number for resource %s' %
                        resourceType
                    )
                episode = Episode(
                    series=self.series,
                    season=season_number,
                    episode=episode_number
                )

                u = url.get(URL, None)
                if u is None:
                    raise ValueError(
                        'Missing URL for resource %s of episode %s' %
                        (resourceType, episode)
                    )

                self.resource_url[resourceType][episode] = u

    @property
    def resourceTypes(self):
        return [t for t in self.resource_url]

    def get_all_resources(self):

        resources = {}

        for resourceType in self.resourceTypes:
            resources[resourceType] = {}

            for episode in self.resource_url[resourceType]:

                logging.info('%s - %s' % (str(episode), resourceType))

                resources[resourceType][episode] = self.get_resource(
                    resourceType, episode)

        return resources


    def get_resource(self, resourceType, episode):
        """

        Parameters
        ----------
        resourceType: str
        episode : `Episode`
        """

        # get method called 'resourceType'
        resourceMethod = getattr(self, resourceType, None)
        if resourceMethod is None:
            error = 'Class %s has no method called %s.' % (
                self.__class__.__name__, resourceType)
            raise ValueError(error)

        # check if URL is available
        url = self.resource_url[resourceType].get(episode, None)
        if url is None:
            return None

        source = self.resource_src[resourceType]

        logging.info('load %s for %s from %s' % (resourceType, episode, url))
        return resourceMethod(url, source=source, episode=episode)
