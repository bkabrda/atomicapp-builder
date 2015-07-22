import os

import anymarkup
from atomic_reactor.util import ImageName
from flexmock import flexmock
import pytest
import requests

from atomicapp_builder.resolver import Resolver

from test.constants import CCCP_INDEX
from test.util import prep_app

# meta images
appone = ImageName(repo='appone')
apptwo = ImageName(repo='apptwo')
appthree = ImageName(repo='appthree')
appfour = ImageName(repo='appfour')

# binary images
apponefoo = ImageName.parse('apponefoo:bar')
appfourfoo1 = ImageName(repo='appfourfoo1')
appfourfoo2 = ImageName(repo='appfourfoo2')
appfourbar1 = ImageName(repo='appfourbar1')

someregistry = 'foo/'
# meta images with registry
appone_reg = ImageName(registry=someregistry, repo='appone')
apptwo_reg = ImageName(registry=someregistry, repo='apptwo')
appthree_reg = ImageName(registry=someregistry, repo='appthree')
appfour_reg = ImageName(registry=someregistry, repo='appfour')

# binary images with registry
apponefoo_reg = ImageName(registry=someregistry, repo='apponefoo', tag='bar')
appfourfoo1_reg = ImageName(registry=someregistry, repo='appfourfoo1')
appfourfoo2_reg = ImageName(registry=someregistry, repo='appfourfoo2')
appfourbar1_reg = ImageName(registry=someregistry, repo='appfourbar1')


class TestResolver(object):
    # TODO: do some more unit testing of other Resolver functions
    @pytest.mark.parametrize('app, branch, meta_expected, binary_expected', [
        ('appone', 'master', set([appone, apptwo, appthree, appfour]),
         set([apponefoo, appfourfoo1, appfourfoo2, appfourbar1])),
        # NOTE: apptwo and appthree intentionally have circular dependency
        ('apptwo', 'stable', set([apptwo, appthree]), set()),
        ('appthree', 'master', set([apptwo, appthree]), set()),
        ('appfour', 'stable', set([appfour]), set([appfourfoo1, appfourfoo2, appfourbar1])),
        # also test top app with "cccp:" prefix; branch is taken from cccp index for these apps
        ('cccp:apptwo', None, set([apptwo, appthree]), set()),
    ])
    def test_full_resolve(self, tmpdir, app, branch, meta_expected, binary_expected):
        if app.startswith('cccp:'):
            app_path = app
        else:
            app_path = prep_app(app, tmpdir, branch)
        if app == 'apptwo':
            app_path = os.path.join(app_path, 'nuleculestuff')

        r = Resolver(app_path, 'file://' + CCCP_INDEX, None, True, str(tmpdir))
        apps = r.resolve()

        # check meta images
        meta_images = set(map(lambda a: a.meta_image.imagename, apps))
        assert meta_images == meta_expected

        binary_images = set()
        for a in apps:
            binary_images.update(map(lambda i: i.imagename, a.binary_images))
        assert binary_images == binary_expected

    @pytest.mark.parametrize(
        'app, branch, meta_built, meta_nonbuilt, binary_built, binary_nonbuilt', [
            ('appone', 'master', set([appfour_reg, appthree_reg]), set([appone_reg, apptwo_reg]),
             set([apponefoo_reg, appfourfoo1_reg]), set([appfourfoo2_reg, appfourbar1_reg])),
            ('appthree', 'master', set([apptwo_reg, appthree_reg]), set([]), set([]), set([])),
        ])
    def test_resolve_when_images_exist(self, tmpdir, app, branch, meta_built, meta_nonbuilt,
                                       binary_built, binary_nonbuilt):
        app_path = prep_app(app, tmpdir, branch)
        r = Resolver(app_path, 'file://' + CCCP_INDEX, someregistry, False, str(tmpdir))
        request_url = 'https://' + someregistry + '/v1/repositories/{0}/tags'
        for b in meta_built | binary_built:
            class X(object):
                status_code = 200
                text = anymarkup.serialize({b.tag if b.tag else 'latest': 'somehash'}, 'json')
            flexmock(requests).should_receive('get').\
                with_args(request_url.format(b.to_str(registry=False, tag=False))).and_return(X())
        for nb in meta_nonbuilt | binary_nonbuilt:
            class Y(object):
                status_code = 404
            flexmock(requests).should_receive('get').\
                with_args(request_url.format(nb.to_str(registry=False, tag=False))).and_return(Y())

        apps = set(r.resolve())
        # check meta images
        exist = set(filter(lambda a: a.meta_image.built is True, apps))
        noexist = apps - exist
        exist = set(map(lambda a: a.meta_image.imagename, exist))
        noexist = set(map(lambda a: a.meta_image.imagename, noexist))
        assert exist == meta_built
        assert noexist == meta_nonbuilt

        # check binary images
        exist = set()
        noexist = set()
        for a in apps:
            exist.update(filter(lambda i: i.built is True, a.binary_images))
            noexist.update(filter(lambda i: i.built is False, a.binary_images))
        exist = set(map(lambda i: i.imagename, exist))
        noexist = set(map(lambda i: i.imagename, noexist))
        assert exist == binary_built
        assert noexist == binary_nonbuilt
