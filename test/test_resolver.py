import os

from atomic_reactor.util import ImageName
from flexmock import flexmock
import pytest
import requests

from atomicapp_builder.resolver import Resolver

from test.constants import CCCP_INDEX
from test.util import prep_app

appone = ImageName(repo='appone')
apptwo = ImageName(repo='apptwo')
appthree = ImageName(repo='appthree')
appfour = ImageName(repo='appfour')

someregistry = 'foo/'
appone_reg = ImageName(registry=someregistry, repo='appone')
apptwo_reg = ImageName(registry=someregistry, repo='apptwo')
appthree_reg = ImageName(registry=someregistry, repo='appthree')
appfour_reg = ImageName(registry=someregistry, repo='appfour')


class TestResolver(object):
    # TODO: do some more unit testing of other Resolver functions
    @pytest.mark.parametrize('app, branch, expected', [
        ('appone', 'master', set([appone, apptwo, appthree, appfour])),
        # NOTE: apptwo and appthree intentionally have circular dependency
        ('apptwo', 'stable', set([apptwo, appthree])),
        ('appthree', 'master', set([apptwo, appthree])),
        ('appfour', 'stable', set([appfour])),
        # also test top app with "cccp:" prefix; branch is taken from cccp index for these apps
        ('cccp:apptwo', None, set([apptwo, appthree])),
    ])
    def test_full_resolve(self, tmpdir, app, branch, expected):
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
        assert meta_images == expected

        # TODO: check binary images

    @pytest.mark.parametrize('app, branch, built, nonbuilt', [
        ('appone', 'master', set([appfour_reg, appthree_reg]), set([appone_reg, apptwo_reg])),
        ('appthree', 'master', set([apptwo_reg, appthree_reg]), set([])),
    ])
    def test_resolve_when_images_exist(self, tmpdir, app, branch, built, nonbuilt):
        app_path = prep_app(app, tmpdir, branch)
        r = Resolver(app_path, 'file://' + CCCP_INDEX, someregistry, False, str(tmpdir))
        request_url = 'https://' + someregistry + '/v1/repositories/{0}/tags'
        for b in built:
            class X(object):
                status_code = 200
            flexmock(requests).should_receive('get').\
                with_args(request_url.format(b.to_str(registry=False, tag=False))).and_return(X())
        for nb in nonbuilt:
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
        assert exist == built
        assert noexist == nonbuilt

        # TODO: check binary images
