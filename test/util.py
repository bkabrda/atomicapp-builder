import os
import subprocess

from test.constants import CCCP_INDEX, FILES, APP_GITURL_TEMPLATE


def prep_app(app, tmpdir, branch):
    subprocess.call(
        ['git', '-C', str(tmpdir), 'clone', APP_GITURL_TEMPLATE.format(app=app),
         app, '-b', branch])
    ret = os.path.join(str(tmpdir), app)
    return ret
