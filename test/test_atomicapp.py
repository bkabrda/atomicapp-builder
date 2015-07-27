import os

import anymarkup
import pytest

from atomicapp_builder.atomicapp import AtomicApp
from atomicapp_builder.exceptions import AtomicappBuilderException

from test.constants import CCCP_INDEX
from test.util import prep_app


class TestAtomicApp(object):
    def setup_method(self, method):
        self.cccp_index = anymarkup.parse_file(CCCP_INDEX)

    def test_init(self, tmpdir):
        a = AtomicApp('cccp:appone', self.cccp_index, None, str(tmpdir))

        # make sure meta_image was created correctly
        assert str(a.meta_image.imagename) == 'appone'
        assert a.meta_image.vcs_url == 'https://github.com/bkabrda/appone.git'
        assert a.meta_image.vcs_type == 'git'
        assert a.meta_image.vcs_local_path == os.path.join(str(tmpdir), 'appone', '.')
        assert a.meta_image.vcs_image_buildfile == 'Dockerfile'
        assert a.meta_image.image_type == 'docker'
        assert a.meta_image.is_meta is True
        assert a.meta_image.build_configs == {
            'stable': 'master',
            'latest': 'master',
        }
        assert a.meta_image.built is False

        # now make sure that other atomicapp attributes are correct
        assert a.appid == 'appone'
        assert a.unprocessed_deps == ['apptwo', 'appfour']

    def test_init_from_path(self, tmpdir):
        path = prep_app('appthree', tmpdir, 'master')
        a = AtomicApp(path, self.cccp_index, None, str(tmpdir))
        # validate that everything worked by looking at the dependency
        assert a.unprocessed_deps == ['apptwo']

    def test_init_fails_for_nonexistent_app(self):
        with pytest.raises(AtomicappBuilderException):
            AtomicApp('cccp:doesntexist', self.cccp_index, None, None)

    def test_process_deps(self, tmpdir):
        a = AtomicApp('cccp:appone', self.cccp_index, None, str(tmpdir))
        a.process_deps(set())
        assert a.unprocessed_deps == []
        assert list(sorted(
            map(lambda a: str(a.meta_image.imagename), a.processed_deps)
        )) == ['appfour', 'apptwo']

    def test_cccp_and_different_Nulecule_name(self, tmpdir):
        path = prep_app('appfour', tmpdir, 'stable')
        a = AtomicApp(path, self.cccp_index, None, str(tmpdir))
        assert a.parsed_cccp['nulecule-file'] == 'newlycool'
        assert a.parsed_nulecule['id'] == 'appfour'
