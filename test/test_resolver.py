import os
import shutil
import tempfile

from dock.util import ImageName
from flexmock import flexmock
import pytest
import requests

from atomicapp_builder.resolver import Resolver

from test.util import prep_app, prep_cccp_index

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
        ('appone', 'master', [appone, apptwo, appthree, appfour]),
        # NOTE: apptwo and appthree intentionally have circular dependency
        ('apptwo', 'stable', [apptwo, appthree]),
        ('appthree', 'master', [apptwo, appthree]),
        ('appfour', 'stable', [appfour]),
        # also test top app with "cccp:" prefix; branch is taken from cccp index for these apps
        ('cccp:apptwo', None, [apptwo, appthree]),
    ])
    def test_full_resolve(self, tmpdir, app, branch, expected):
        if app.startswith('cccp:'):
            app_path = app
        else:
            app_path = prep_app(app, tmpdir, branch)
        if app == 'apptwo':
            app_path = os.path.join(app_path, 'nuleculestuff')
        cccp_index = prep_cccp_index(tmpdir)

        r = Resolver(app_path, cccp_index, None, True, str(tmpdir))
        built, nonbuilt = r.resolve()
        assert built == {}
        for k, v in nonbuilt.items():
            assert k in expected
            exp_path = os.path.join(str(tmpdir), k.repo)
            if k == apptwo:
                exp_path = os.path.join(exp_path, 'nuleculestuff')
            # workaround the ending slash that may or may not be there
            exp_paths = [exp_path, exp_path + '/']
            assert v in exp_paths

    @pytest.mark.parametrize('app, branch, built, nonbuilt', [
        ('appone', 'master', [appfour_reg, appthree_reg], [appone_reg, apptwo_reg]),
        ('appthree', 'master', [apptwo_reg, appthree_reg], []),
    ])
    def test_resolve_when_images_exist(self, tmpdir, app, branch, built, nonbuilt):
        cccp_index = prep_cccp_index(tmpdir)
        app_path = prep_app(app, tmpdir, branch)
        r = Resolver(app_path, cccp_index, someregistry, False, str(tmpdir))
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

        res_built, res_nonbuilt = r.resolve()
        assert len(res_built) == len(built)
        assert len(res_nonbuilt) == len(nonbuilt)
        # the checkout functionality is already done above, let's just check correct resolving
        for b in res_built:
            assert b in built
        for nb in res_nonbuilt:
            assert nb in nonbuilt
