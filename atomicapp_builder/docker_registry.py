import logging

import requests

from atomicapp_builder import exceptions

logger = logging.getLogger(__name__)


class DockerRegistry(object):
    def __init__(self, url, insecure=False):
        self.url = url
        self.insecure = insecure

    def has_image(self, image):
        # TODO: it seems that the best non-auth way is to look at repository's tags,
        #  e.g. registry.com/v1/repositories/<image>/tags
        url = ('http://' if self.insecure else 'https://') + self.url
        url = url + '/v1/repositories/{0}/tags'.format(image.to_str(registry=False, tag=False))
        ret = False
        try:
            logger.debug('Polling {0} to see if image {1} exists'.format(url, image))
            r = requests.get(url)
            if r.status_code == 200:
                logger.debug('Image {0} exists'.format(image))
                ret = True
            else:
                logger.debug('Image {0} does not exist'.format(image))
        except requests.exceptions.SSLError as e:
            raise exceptions.AtomicappBuilderException(
                    'SSL error while polling registry: {0}'.format(e))
        except Exception as e:
            logger.debug('Image {0} does not seem to exist, exception was: {1}'.format(image, e))

        return ret
