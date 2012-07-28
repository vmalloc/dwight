import os
import platform
import re
import tempfile
from dwight_chroot.include import Include
from dwight_chroot.platform_utils import execute_command_assert_success
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
        # this is necessary for capturing output of chrooted commands
        self.environment.config["INCLUDES"].append(Include("/tmp", "/tmp"))
        self.environment.config["PWD"] = "/var"
        self.environment.config["NUM_LOOP_DEVICES"] = 8
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
    def test__uid(self):
        self.environment.config["UID"] = 0
        self.assertChrootUid(0)
    def test__sudo_uid_by_default(self):
        self.assertIsNone(self.environment.config["UID"])
        self.assertIn("SUDO_UID", os.environ)
        self.assertChrootUid(int(os.environ["SUDO_UID"]))
    def test__gid(self):
        self.environment.config["GID"] = 0
        self.assertChrootGid(0)
    def test__sudo_gid_by_default(self):
        self.assertIsNone(self.environment.config["GID"])
        self.assertIn("SUDO_GID", os.environ)
        self.assertChrootGid(int(os.environ["SUDO_GID"]))
    def test__pwd(self):
        self.assertChrootOutput("pwd", self.environment.config["PWD"] + "\n")
    def test__num_loop_devices(self):
        self.environment.config["NUM_LOOP_DEVICES"] = 20
        for loop_device in self.get_all_loop_devices():
            os.unlink(loop_device)
        self.assertChrootSuccess()
        loop_devices = self.get_all_loop_devices()
        self.assertEquals(len(loop_devices), self.environment.config["NUM_LOOP_DEVICES"])
    def get_all_loop_devices(self):
        return [os.path.join("/dev", filename) 
                for filename in os.listdir("/dev") 
                if re.match(r"loop\d+", filename)]
    def assertMountSuccessful(self, name):
        self.assertChrootFileExists("/mounts/{0}/{0}_file".format(name))
    def assertChrootFileExists(self, path):
        returncode = self.environment.run_command_in_chroot("test -e {}".format(path))
        self.assertEquals(returncode, 0, "File {0!r} does not exist".format(path))
    def assertChrootUid(self, id):
        self.assertChrootOutput("id -u", str(id) + "\n")
    def assertChrootGid(self, id):
        self.assertChrootOutput("id -g", str(id) + "\n")
    def assertChrootOutput(self, cmd, output):
        output_file_path = "/tmp/__dwight_testing_output"
        if os.path.exists(output_file_path):
            os.unlink(output_file_path)
        returncode = self.environment.run_command_in_chroot("{0} > {1}".format(cmd, output_file_path))
        self.assertEquals(returncode, 0)
        with open(output_file_path, "r") as output_file:
            self.assertEquals(output_file.read(), output)
    def assertChrootSuccess(self):
        self.assertEquals(0, self.environment.run_command_in_chroot("true"))
