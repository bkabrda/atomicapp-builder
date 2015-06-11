import logging

import requests

logger = logging.getLogger(__name__)


class DockerRegistry(object):
    def __init__(self, url):
        self.url = url

    def has_image(self, image):
        # TODO: it seems that the best non-auth way is to look at repository's tags,
        #  e.g. registry.com/v1/repositories/<image>/tags
        url = self.url + '/v1/repositories/{0}/tags'.format(image.to_str(registry=False, tag=False))
        ret = False
        try:
            logger.debug('Polling {0} to see if image {1} exists'.format(url, image))
            r = requests.get(url)
            if r.status_code == 200:
                ret = True
        except Exception as e:
            logger.debug('Image {0} does not seem to exist, exception was: {1}'.format(image, e))

        return ret
