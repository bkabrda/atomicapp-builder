import logging
import os
import subprocess

import anymarkup
from atomic_reactor.util import ImageName

from atomicapp_builder.exceptions import AtomicappBuilderException
from atomicapp_builder.imageinfo import ImageInfo


logger = logging.getLogger(__name__)


class AtomicApp(object):
    def __init__(self, app_path, cccp_index, local_registry_uri, tmpdir):
        self.app_path = app_path
        self.cccp_index = cccp_index
        self.cccp_index_entry = None
        self.local_registry_uri = local_registry_uri
        self.tmpdir = tmpdir

        if self.app_path.startswith('cccp:'):
            self.appid = self.app_path[len('cccp:'):]
            self.app_path = self.checkout()

        self.parse_cccp()
        self.parse_nulecule()

        self.appid = self.parsed_nulecule['id']

        # first, construct the ImangeName for meta image and then meta image itself
        meta_image_name = ImageName(registry=self.local_registry_uri, repo=self.appid)
        self.meta_image = ImageInfo(
            imagename=meta_image_name,
            vcs_url=self.find_cccp_index_entry()['git-url'],
            vcs_type='git',
            vcs_local_path=os.path.dirname(self.nulecule_file),
            # for meta image, buildconfig always looks like this
            build_configs={
                'stable': self.find_cccp_index_entry()['git-branch'],
                'latest': self.find_cccp_index_entry()['git-branch'],
            },
            is_meta=True,
        )

        self.binary_images = []
        self.deps_were_processed = False
        self.unprocessed_deps = []
        self.processed_deps = []
        graph = self.parsed_nulecule['graph']
        for item in graph:
            if 'source' in item:  # if 'source' is there, it's a dependency
                self.unprocessed_deps.append(item['name'])
            elif 'images' in item:  # else we process binary images
                self.process_binary_images(item)
            else:
                pass  # nothing to process in this item - TODO is this an error?

    def find_cccp_index_entry(self):
        if self.cccp_index_entry is None:
            for entry in self.cccp_index['Projects']:
                if entry['app-id'] == self.appid:
                    self.cccp_index_entry = entry
                    break
            if self.cccp_index_entry is None:
                raise AtomicappBuilderException(
                    'App "{0}" not found in index, cannot proceed'.format(self.appid))
            if 'git-branch' not in self.cccp_index_entry:
                self.cccp_index_entry['git-branch'] = 'master'

        return self.cccp_index_entry

    def checkout(self):
        entry = self.find_cccp_index_entry()
        try:
            logger.debug('Checking out application %s', self.appid)
            cmd = ['git', '-C', self.tmpdir, 'clone', entry['git-url'], self.appid]
            if 'git-branch' in entry and entry['git-branch']:
                cmd.extend(['-b', entry['git-branch']])
            subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            logger.debug(
                'Application %s checked out at %s',
                self.appid, os.path.join(self.tmpdir, self.appid))
        except (OSError, subprocess.CalledProcessError) as ex:
            raise AtomicappBuilderException(ex)

        self.local_path = os.path.join(self.tmpdir, self.appid)
        return os.path.join(self.local_path, entry['git-path'] or '')

    def parse_nulecule(self):
        self.nulecule_file = os.path.join(
            self.app_path,
            self.parsed_cccp.get('nulecule-file', 'Nulecule')
        )
        if not os.path.exists(self.nulecule_file):
            raise AtomicappBuilderException(
                'Nulecule file "{0}" doesn\'t exist'.format(self.nulecule_file))
        self.parsed_nulecule = anymarkup.parse_file(self.nulecule_file)

    def parse_cccp(self):
        self.cccp_path = os.path.join(self.app_path, '.cccp.yml')
        if not os.path.exists(self.cccp_path):
            self.cccp_path = os.path.join(self.app_path, 'cccp.yml')
        # if cccp file doesn't exist, just silently skip it
        self.parsed_cccp = {}
        if os.path.exists(self.cccp_path):
            self.parsed_cccp = anymarkup.parse_file(self.cccp_path)
        print(self.parsed_cccp)

    def process_binary_images(self, graph_item):
        images = graph_item['images']
        for img in images:
            kwargs = {}
            # we'll only pass arguments that are provided in Nulecule file
            for k in ['vcs_url', 'vcs_type', 'vcs_image_buildfile', 'image_type', 'build_configs']:
                if k in img:
                    kwargs[k] = img[k]
            kwargs['imagename'] = ImageName.parse(img['name'])
            # for now, we just replace the registry with our local one
            # TODO: maybe use it just for images that don't have any registry?
            kwargs['imagename'].registry = self.local_registry_uri
            self.binary_images.append(ImageInfo(**kwargs))

    def process_deps(self, globally_processed):
        # TODO: what to do with deps marked as "skip" in .cccp.yaml?
        """Process deps of current app (not recursive)."""
        if self.deps_were_processed:
            return

        while len(self.unprocessed_deps) > 0:
            dep = self.unprocessed_deps.pop()
            # if the dep was already processed globally, just reuse it
            found = None
            for gp in globally_processed:
                if gp.appid == dep:
                    found = gp
            if found:
                self.processed_deps.append(found)
            else:
                self.processed_deps.append(type(self)(
                    'cccp:' + dep,
                    self.cccp_index,
                    self.local_registry_uri,
                    self.tmpdir)
                )

        self.deps_were_processed = True

    def __lt__(self, other):
        return self.appid < other.appid
