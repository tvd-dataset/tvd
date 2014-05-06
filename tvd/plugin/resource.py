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

URL = 'url'
SEASON = 'season'
EPISODE = 'episode'
SOURCE = 'source'
from __future__ import unicode_literals


import logging
import requests
from tvd.core.episode import Episode
from tvd.core.time import TFloating
import requests
import sys


class ResourceMixin(object):

    def init_resource(self, www):

        # initialize web resources data structure
        # resources[episode] contains all resources for a given episode
        self.resources = {}

        # loop on web resources described in 'www' section
        for resource_type, resource in www.iteritems():

            if 'source' in resource:
                message = \
"""IN CASE YOU USE '{resource}' RESOURCES, PLEASE CONSIDER CITING:
{reference}
"""
                sys.stdout.write(message.format(
                    resource=resource_type, reference=resource['source']))

            # obtain corresponding 'get_resource' method
            resource_method = self._get_resource_method(resource_type)

            # read resource 'source' from YAML configuration when provided
            source = resource.get(SOURCE, None)

            # loop on all provided URLs
            # NB: some episodes might not have some resources
            for url in resource.get(URL, []):

                season_number = url[SEASON]
                episode_number = url[EPISODE]
                episode = Episode(
                    series=self.__class__.__name__,
                    season=season_number,
                    episode=episode_number
                )

                # add episode to resource main structure
                # in case it is the first time it is encountered
                if episode not in self.resources:
                    self.resources[episode] = {}

                # initialize resource placeholder
                #
                self.resources[episode][resource_type] = {
                    # method to call to get the resource
                    'method': resource_method,
                    # parameters to pass to method to get the resource
                    'params': {
                        'url': url[URL],
                        'source': source,
                        'episode': episode
                    },
                    # results of call "method(**params)"
                    # NB: it is set to None until we actually get this resource
                    'result': None
                }

    def _get_resource_method(self, resource_type):
        """Get method for given resource

        resource_type : str
            Resource type, as provided in YAML configuration file

        Returns
        -------
        method : callable
            Method defined in inheriting plugin to be used
            to obtain `resource_type` resource

        """
        resource_method = getattr(self, resource_type, None)

        if resource_method is None:

            error = 'Class %s has no method called %s.' % (
                self.__class__.__name__, resource_type)

            raise ValueError(error)

        return resource_method

    def has_resource(self, resource_type, episode):
        """
        Checks whether resource `resource_type` exists
        for given `episode`

        Parameters
        ----------
        resource_type : str
        episode : `tvd.Episode`
        """

        resources = self.resources.get(episode, None)
        if resources is None:
            return False

        resource = resources.get(resource_type, None)
        if resource is None:
            return False

        return True
    
    def get_resource(self, resource_type, episode, update=False):
        """

        Parameters
        ----------
        resource_type: str
        episode : `Episode`
        update : bool, optional
            When True, force re-downloading of resources
        """

        if not self.has_resource(resource_type, episode):
            error = 'Episode {episode} has no resource "{resource_type}"'
            raise ValueError(error.format(
                episode=episode,
                resource_type=resource_type)
            )

        resource = self.resources[episode][resource_type]

        result = resource['result']
        if update or result is None:
            method = resource['method']
            params = resource['params']

            msg = 'updating "{ep:s}" "{rsrc:s}"'
            logging.debug(msg.format(ep=episode, rsrc=resource_type))

            TFloating.reset()
            result = method(**params)

            result.graph['plugin'] = \
                sys.modules[self.__class__.__module__].__version__

            self.resources[episode][resource_type]['result'] = result

        return result

    def iter_resources(self, resource_type=None, episode=None, data=False):
        """Resource iterator

        Resources are yielded in episode chronological order
        and resource name alphabetical order

        Parameters
        ----------
        resource_type : str, optional
            When provided, only iterate over this resource type
        episode : `tvd.Episode`, optional
            When provided, only iterate over resources for this episode
        data : boolean, optional
            Whether to yield actual data

        Returns
        -------
        (episode, resource_type[, data]) iterator
        """

        # loop on episodes in airing chronological order
        for _episode in sorted(self.resources):

            # skip this episode if not requested
            if (episode is not None) and \
               (episode != _episode):
                continue

            # loop on resources in name alphabetical order
            for _resource_type in sorted(self.resources[_episode]):

                # skip this resource if not requested
                if (resource_type is not None) and \
                   (resource_type != _resource_type):
                    continue

                # really get this resource
                if data:
                    _data = self.get_resource(
                        _resource_type,
                        _episode,
                        update=True
                    )
                    yield _episode, _resource_type, _data

                else:
                    yield _episode, _resource_type

    def get_all_resources(self, update=False):

        resources = {}

        for episode, resource_type in self.iter_resources(
            resource_type=None, episode=None, data=False
        ):

            if episode not in resources:
                resources[episode] = {}

            resource = self.get_resource(resource_type, episode, update=update)

            resources[episode][resource_type] = resource

        return resources

    CHARACTER_MAPPING = {
        # hyphen
        ord(u'\u2013'): u"-",    # –
        ord(u'\u2014'): u"-",    # —
        # quote
        ord(u'\u2018'): u"'",    # ‘
        ord(u'\u2019'): u"'",    # ’
        # double-quote
        ord(u'\u201c'): u'"',    # “
        ord(u'\u201d'): u'"',    # ”
        # space
        ord(u'\u200b'): u" ",    #    
        ord(u'\xa0'): u" ",      #
        # other
        ord(u'\u2026'): u"...",  # …
        # ord(u'\xe9'): u"é"
    }

    HTML_MAPPING = {
        # hyphen
        u"&#8211;": u"-",
        # quote
        u"&#8216;": u"'",
        u"&#8217;": u"'",
        u"&quot;": '"',
        # double-quote
        u"&#8220;": u'"',
        u"&#8221;": u'"',
        # other
        u"&#8230;": u"..."
    }

    def download_as_utf8(self, url):
        """Download webpage content as UTF-8

        Parameters
        ----------
        url : str
            Webpage URL
        mapping : dict
            Translation table (mapping of Unicode ordinals to Unicode ordinals
            or to Unicode strings).
        Returns
        -------
        text : unicode
            Webpage content as unicode UTF-8 text

        """

        # request URL content with dummy user-agent
        user_agent = {'User-agent': 'TVD'}
        r = requests.get(url, headers=user_agent)
        
        # get content as UTF-8 unicode
        r.encoding = 'UTF-8'
        udata = r.text
        
        # apply mapping tables
        udata = udata.translate(self.CHARACTER_MAPPING)
        for old, new in self.HTML_MAPPING.iteritems():
            udata = udata.replace(old, new)

        return udata
