import logging

import requests

from atomicapp_builder import exceptions

logger = logging.getLogger(__name__)


class DockerRegistry(object):
    def __init__(self, url, insecure=False):
        self.url = url
        self.insecure = insecure

    def has_image(self, imageinfo):
        # TODO: it seems that the best non-auth way is to look at repository's tags,
        #  e.g. registry.com/v1/repositories/<image>/tags
        url = ('http://' if self.insecure else 'https://') + self.url
        url = url + '/v1/repositories/{0}/tags'.format(
            imageinfo.name_str(registry=False, tag=False))
        ret = False
        try:
            logger.debug('Polling %s to see if image %s exists', url, imageinfo.name_str())
            r = requests.get(url)
            if r.status_code == 200:
                logger.debug('Image %s exists', imageinfo.name_str())
                ret = True
            else:
                logger.debug('Image %s does not exist', imageinfo.name_str())
        except requests.exceptions.SSLError as e:
            raise exceptions.AtomicappBuilderException('SSL error while polling registry: %s', e)
        except Exception as e:
            logger.debug(
                'Image %s does not seem to exist, exception was: %s',
                imageinfo.name_str(), e)

        return ret
