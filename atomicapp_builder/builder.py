import logging
import os

import atomic_reactor
from atomic_reactor import api as arapi

import atomicapp_builder

logger = logging.getLogger(__name__)


class Builder(object):
    def __init__(self, build_image, image_info, tag=None,
                 registry=None, registry_insecure=False):
        self.build_image = build_image
        self.image_info = image_info
        self.tag = tag
        self.registry = registry
        self.registry_insecure = registry_insecure

    def build(self):
        """Build Docker image from ImageInfo object using atomic_reactor. Set ImageInfo
        object `built` and `build_result` attributes.

        :return: atomic_reactor's BuildResults object
        """
        tag = self.tag or self.image_info.name_str()
        df_dir = os.path.join(self.image_info.vcs_local_path, self.image_info.vcs_image_buildfile)
        df_dir = os.path.dirname(df_dir)
        target_registries = [self.registry] if self.registry else None

        # atomic_reactor's logging during build isn't really useful, send it to logfile only
        atomic_reactor.set_logging(level=logging.DEBUG, handler=atomicapp_builder.file_handler)
        logger.info('Building image %s ...', tag)
        response = arapi.build_image_using_hosts_docker(
            self.build_image,
            {'provider': 'path', 'uri': 'file://' + df_dir},
            tag,
            target_registries=target_registries,
            target_registries_insecure=self.registry_insecure
        )
        self.image_info.build_result = response
        if response.return_code == 0:
            self.image_info.built = True
        return self.image_info.built
