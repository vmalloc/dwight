import os
import platform
import tempfile
from .test_utils import EnvironmentTestCase

class ChrootingTestCase(EnvironmentTestCase):
    def setUp(self):
        super(ChrootingTestCase, self).setUp()
        if os.getuid() != 0:
            self.skipTest("Not root")
        if platform.system() != "Linux":
            self.skipTest("Not linux")
        with open(os.path.join(os.path.dirname(__file__), "..", "example_config.py"), "r") as example_config:
            self.environment.config.load_from_string(example_config.read())
    def test__root_image(self):
        self.assertChrootFileExists("/dwight_base_image_file")
    def test__include_local_path(self):
        self.assertMountSuccessful("fetched_from_local_path")
    def test__include_http(self):
        self.assertMountSuccessful("fetched_from_http")
    def test__include_git(self):
        self.assertMountSuccessful("fetched_from_git")
    def test__include_mercurial(self):
        self.assertMountSuccessful("fetched_from_hg")
    def test__include_git_branch(self):
        self.assertMountSuccessful("fetched_from_git_branch")
    def test__include_mercurial_branch(self):
        self.assertMountSuccessful("fetched_from_hg_branch")
    def assertMountSuccessful(self, name):
        self.assertChrootFileExists("/mounts/{0}/{0}_file".format(name))
    def assertChrootFileExists(self, path):
        returncode = self.environment.run_command_in_chroot("test -e {}".format(path))
        self.assertEquals(returncode, 0, "File {0!r} does not exist".format(path))
