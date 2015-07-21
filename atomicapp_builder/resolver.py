import logging

import anymarkup
import requests

from atomicapp_builder.docker_registry import DockerRegistry
from atomicapp_builder.atomicapp import AtomicApp

logger = logging.getLogger(__name__)


class Resolver(object):
    def __init__(self, top_app, cccp_index_uri, docker_registry_url, registry_insecure, tmpdir):
        self.top_app = top_app
        self.cccp_index_uri = cccp_index_uri
        self.tmpdir = tmpdir
        self.docker_registry_url = docker_registry_url
        self.registry_insecure = registry_insecure
        if docker_registry_url:
            self.docker_registry = \
                DockerRegistry(docker_registry_url, registry_insecure)
        else:
            self.docker_registry = None
        self.cccp_index = None

    def read_cccp_index(self):
        if self.cccp_index_uri.startswith('file://'):
            file_to_read = self.cccp_index_uri[len('file://'):]
            self.cccp_index = anymarkup.parse_file(file_to_read)
        else:
            fetched = requests.get(self.cccp_index_uri)
            self.cccp_index = anymarkup.parse(fetched.text)

    def check_images_exist(self, apps):
        """Checks if images exist for given iterable of AtomicApps, sets the `built` attribute
        correctly for all images of these AtomicApps.
        """
        for app in apps:
            #TODO: check binary images
            # check only local registry for meta images
            if self.docker_registry and self.docker_registry.has_image(app.meta_image):
                app.meta_image.built = True

    def resolve(self):
        """Resolve inter-app dependencies recursively and check whether meta and binary images
        exist.

        :return: List of AtomicApp objects with resolved binary images and dependencies
        """
        self.read_cccp_index()
        unresolved = set(
            [AtomicApp(self.top_app, self.cccp_index, self.docker_registry_url, self.tmpdir)]
        )
        resolved = set()
        while len(unresolved) > 0:
            app = unresolved.pop()
            app.process_deps(resolved)
            resolved.add(app)
            for dep in app.processed_deps:
                if dep.appid not in map(lambda a: a.appid, resolved):
                    unresolved.add(dep)

        self.check_images_exist(resolved)

        return list(sorted(resolved))
