import os
import shutil
import tempfile

import pytest

from atomicapp_builder.resolver import Resolver

from test.util import prep_app, prep_cccp_index


class TestResolver(object):
    # TODO: do some more unit testing of other Resolver functions
    @pytest.mark.parametrize('app, branch, expected', [
        ('appone', 'master', ['appone', 'apptwo', 'appthree', 'appfour']),
        # NOTE: apptwo and appthree intentionally have circular dependency
        ('apptwo', 'stable', ['apptwo', 'appthree']),
        ('appthree', 'master', ['apptwo', 'appthree']),
        ('appfour', 'stable', ['appfour']),
        # also test top app with "cccp:" prefix; branch is taken from cccp index for these apps
        ('cccp:apptwo', None, ['apptwo', 'appthree']),
    ])
    def test_full_resolve(self, tmpdir, branch, app, expected):
        if app.startswith('cccp:'):
            app_path = app
        else:
            app_path = prep_app(app, tmpdir, branch)
        if app == 'apptwo':
            app_path = os.path.join(app_path, 'nuleculestuff')
        cccp_index = prep_cccp_index(tmpdir)
        r = Resolver(app_path, cccp_index, str(tmpdir))
        result = r.resolve()
        for k, v in result.items():
            assert k in expected
            exp_path = os.path.join(str(tmpdir), k)
            if k == 'apptwo':
                exp_path = os.path.join(exp_path, 'nuleculestuff')
            # workaround the ending slash that may or may not be there
            exp_paths = [exp_path, exp_path + '/']
            assert v in exp_paths
