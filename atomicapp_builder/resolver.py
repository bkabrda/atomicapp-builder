import os
import subprocess

import anymarkup
import requests

from atomicapp_builder import exceptions


class Resolver(object):
    def __init__(self, top_app, cccp_index_uri, tmpdir):
        self.top_app = top_app
        self.cccp_index_uri = cccp_index_uri
        self.tmpdir = tmpdir
        self.cccp_index = None

    def read_cccp_index(self):
        if self.cccp_index_uri.startswith('file://'):
            file_to_read = self.cccp_index_uri[len('file://'):]
            self.cccp_index = anymarkup.parse_file(file_to_read)
        else:
            fetched = requests.get(self.cccp_index_uri)
            self.cccp_index = anymarkup.parse(fetched.text)

    def read_nulecule(self, path):
        """Return id of this app and it's graph. The returned graph is in form
        {<name>: <other_graph_object_attrs>}.
        """
        # TODO: can be named differently; inspect .cccp.yaml to find out
        nlc_content = anymarkup.parse_file(os.path.join(path, 'Nulecule'))
        # TODO: we want to implement graph as object and hide details and potential
        #  differencies in Nulecule spec versions behind it
        appid = nlc_content['id']
        graph = nlc_content['graph']
        appgraph = {}
        for item in graph:
            key = item.pop('name')
            appgraph[key] = item
        return appid, appgraph

    def checkout_app(self, appid):
        found = None
        for entry in self.cccp_index['Projects']:
            if entry['app-id'] == appid:
                found = entry
                break

        if found is None:
            raise exceptions.AtomicappBuilderException(
                'Project "{0}" not found in index, cannot proceed'.format(appid))

        try:
            cmd = ['git', '-C', self.tmpdir, 'clone', found['git-url'], appid]
            if 'git-branch' in found and found['git-branch']:
                cmd.extend(['-b', found['git-branch']])
            subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except (OSError, subprocess.CalledProcessError):
            raise  # TODO: handle?

        return os.path.join(self.tmpdir, appid, found['git-path'] or '')

    def get_appids_to_build(self, top_app):
        this_appid, alldeps = self.read_nulecule(top_app)
        to_build = {this_appid: top_app}
        while len(alldeps) > 0:
            depid, depattrs = alldeps.popitem()
            if 'source' in depattrs:  # if 'source' is there, it's a dep that we must check
                # TODO: check if it's in provided registry or not
                # TODO: if it's in the provided registry, can we be sure that all it's deps are?
                # TODO: what to do with deps marked as "skip" in .cccp.yaml
                if depid not in to_build:
                    dep_path = self.checkout_app(depid)
                    to_build[depid] = dep_path
                    alldeps.update(self.read_nulecule(dep_path)[1])
        return to_build

    def resolve(self):
        self.read_cccp_index()
        if self.top_app.startswith('cccp:'):
            top_app_path = self.checkout_app(self.top_app[len('cccp:'):])
        else:
            top_app_path = self.top_app

        return self.get_appids_to_build(top_app_path)
