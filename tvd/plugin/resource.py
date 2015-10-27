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

import six
import logging
import requests
from ..core import Episode
from ..core.json import load as load_json
from pyannote.core import T
import sys


TVD_RESOURCE_URL = 'url'
TVD_RESOURCE_SEASON = 'season'
TVD_RESOURCE_EPISODE = 'episode'
TVD_RESOURCE_SOURCE = 'source'
TVD_RESOURCE_TYPE = 'type'
TVD_ACKNOWLEDGEMENT = """
IN CASE YOU USE '{resource}' RESOURCES, PLEASE CONSIDER CITING:
{reference}
"""


class ResourceMixin(object):

    def init_resource(self, resources):

        # initialize web resources data structure
        # resources[episode] contains all resources for a given episode
        self.resources = {}

        # loop on web resources described in 'resources' section
        for resource_type, resource in six.iteritems(resources):

            if 'source' in resource:
                sys.stdout.write(TVD_ACKNOWLEDGEMENT.format(
                    resource=resource_type, reference=resource['source']))

            # obtain corresponding 'get_resource' method
            resource_method = self._get_resource_method(resource_type)

            # read resource 'source' from YAML configuration when provided
            source = resource.get(TVD_RESOURCE_SOURCE, None)

            # read resource 'type' from YAML configuration when provided
            data_type = resource.get(TVD_RESOURCE_TYPE, None)

            # loop on all provided URLs
            # NB: some episodes might not have some resources
            for url in resource.get(TVD_RESOURCE_URL, []):

                season_number = url[TVD_RESOURCE_SEASON]
                episode_number = url[TVD_RESOURCE_EPISODE]
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
                self.resources[episode][resource_type] = {
                    # method to call to get the resource
                    'method': resource_method,
                    # parameters to pass to method to get the resource
                    'params': {
                        'url': url[TVD_RESOURCE_URL],
                        'source': source,
                        'episode': episode
                    },
                    # results of call "method(**params)"
                    # NB: it is set to None until we actually get this resource
                    'result': None,
                    # data type (transcription, annotation, else ?)
                    'type': data_type
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

    def get_resource_from_disk(self, resource_type, episode):
        """Load resource from disk, sotre it in memory and return it

        Parameters
        ----------
        episode : Episode
            Episode
        resource_type : str
            Type of resource

        Returns
        -------
        resource : Timeline, Annotation or Transcription
            Resource of type `resource_type` for requested episode

        Raises
        ------
        Exception
            If the resource is not available on disk

        """

        msg = 'getting {t:s} for {e:s} from disk'
        logging.debug(msg.format(e=episode, t=resource_type))

        path = self.path_to_resource(episode, resource_type)
        result = load_json(path)

        msg = 'saving {t:s} for {e:s} into memory'
        logging.debug(msg.format(e=episode, t=resource_type))

        self.resources[episode][resource_type]['result'] = result

        return result

    def get_resource_from_memory(self, resource_type, episode):
        """Load resource from memory

        Parameters
        ----------
        episode : Episode
            Episode
        resource_type : str
            Type of resource

        Returns
        -------
        resource : Timeline, Annotation or Transcription
            Resource of type `resource_type` for requested episode

        Raises
        ------
        Exception
            If the resource is not available in memory
        """

        msg = 'getting {t:s} for {e:s} from memory'
        logging.debug(msg.format(e=episode, t=resource_type))

        result = self.resources[episode][resource_type]['result']

        if result is None:
            msg = 'resource {t:s} for {e:s} is not available in memory'
            raise ValueError(msg.format(e=episode, t=resource_type))

        return result

    def get_resource_from_plugin(self, resource_type, episode):
        """Load resource from plugin, store it in memory and return it

        Parameters
        ----------
        episode : Episode
            Episode
        resource_type : str
            Type of resource

        Returns
        -------
        resource : Timeline, Annotation or Transcription
            Resource of type `resource_type` for requested episode

        Raises
        ------
        Exception
            If plugin failed to provide the requested resource
        """

        msg = 'getting {t:s} for {e:s} from plugin'
        logging.debug(msg.format(e=episode, t=resource_type))

        resource = self.resources[episode][resource_type]
        method = resource['method']
        params = resource['params']

        T.reset()
        result = method(**params)

        msg = 'saving {t:s} for {e:s} into memory'
        logging.debug(msg.format(e=episode, t=resource_type))

        self.resources[episode][resource_type]['result'] = result

        return result

    def get_resource(self, resource_type, episode, update=False):
        """Get resource

        Parameters
        ----------
        resource_type: str
        episode : Episode
        update : bool, optional

        Returns
        -------
        resource : Timeline, Annotation or Transcription
            Resource of type `resource_type` for requested `episode`

        Raises
        ------
        ValueError
            If plugin failed to provide the requested resource.

        """

        result = None

        if update:
            funcs = [self.get_resource_from_plugin]

        else:
            funcs = [self.get_resource_from_memory,
                     self.get_resource_from_disk,
                     self.get_resource_from_plugin]

        for func in funcs:
            try:
                result = func(resource_type, episode)
                break

            except:
                continue

        if result is None:
            error = 'cannot get {t:s} for episode {e:s}'
            raise ValueError(error.format(t=resource_type, e=episode))

        return result

    def iter_resources(self, resource_type=None, episode=None,
                       data=False, update=True):
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
                    _data = self.get_resource(_resource_type, _episode,
                                              update=update)
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

    def clean_text(self, udata):

        # apply mapping tables
        udata = udata.translate(self.CHARACTER_MAPPING)
        for old, new in six.iteritems(self.HTML_MAPPING):
            udata = udata.replace(old, new)
        return udata

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

        return self.clean_text(r.text)
