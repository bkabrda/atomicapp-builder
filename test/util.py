import os
import shutil
import subprocess

from test.constants import CCCP_INDEX, FILES, APP_GITURL_TEMPLATE


def prep_app(app, tmpdir, branch):
    subprocess.call(
        ['git', '-C', str(tmpdir), 'clone', APP_GITURL_TEMPLATE.format(app=app),
         app, '-b', branch])
    ret = os.path.join(str(tmpdir), app)
    return ret

def prep_cccp_index(tmpdir):
    with open(CCCP_INDEX) as f:
        index = f.read()
    cccp_index = os.path.join(str(tmpdir), 'cccpindex.yaml')
    with open(cccp_index, 'w') as f:
        to_write = index.replace('TESTFILESPATH', FILES)
        f.write(to_write) 
    return 'file://' + cccp_index
