import logging

import atomic_reactor
from atomic_reactor import api as arapi

import atomicapp_builder

logger = logging.getLogger(__name__)


class Builder(object):
    def __init__(self, build_image, df_path, image_name, tag=None,
                 registry=None, registry_insecure=False):
        self.build_image = build_image
        self.df_path = df_path
        self.image_name = image_name
        self.tag = tag
        self.registry = registry
        self.registry_insecure = registry_insecure

    def build(self):
        """Build Docker image using atomic_reactor.

        :return: atomic_reactor's BuildResults object
        """
        tag = self.tag or self.image_name.to_str()
        target_registries = [self.registry] if self.registry else None

        # atomic_reactor's logging during build isn't really useful, send it to logfile only
        atomic_reactor.set_logging(level=logging.DEBUG, handler=atomicapp_builder.file_handler)
        logger.info('Building image %s ...', tag)
        response = arapi.build_image_using_hosts_docker(
            self.build_image,
            {'provider': 'path', 'uri': 'file://' + self.df_path},
            tag,
            target_registries=target_registries,
            target_registries_insecure=self.registry_insecure
        )

        return response
