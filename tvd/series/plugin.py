import yaml
import logging
from pkg_resources import resource_filename

from tvd.common.episode import Episode

CONFIG_HUMAN_READABLE_NAME = 'name'
CONFIG_ORIGINAL_LANGUAGE = 'language'
CONFIG_WEB_RESOURCES = 'www'

SOURCE = 'source'
URL = 'url'
SEASON = 'season'
EPISODE = 'episode'


class SeriesPlugin(object):

    def __init__(self):

        super(SeriesPlugin, self).__init__()

        # obtain path to YAML configuration file and load it
        path = resource_filename(self.series, '%s.yml' % self.series)
        with open(path, mode='r') as f:
            config = yaml.load(f)

        # human readable name is obtained from YAML configuration file
        self.name = config[CONFIG_HUMAN_READABLE_NAME]

        # original language is obtained from YAML configuration file
        self.language = config[CONFIG_ORIGINAL_LANGUAGE]

        self.resource_url = {}
        self.resource_src = {}

        # web resources
        www = config[CONFIG_WEB_RESOURCES]
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
    def series(self):
        return self.__class__.__name__

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
