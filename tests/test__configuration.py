from .test_utils import EnvironmentTestCase
import os
from tempfile import mkdtemp
from dwight_chroot.exceptions import (
    CannotLoadConfiguration,
    InvalidConfiguration,
    UnknownConfigurationOptions,
    )

class ConfigurationLoadingTest(EnvironmentTestCase):
    def test__bad_configuration_strings(self):
        for bad_source_string in [
                "kjlkj;;:::",
                "for in import",
                ",,",
        ]:
            with self.assertRaises(CannotLoadConfiguration):
                self.environment.config.load_from_string(bad_source_string)
    def test__base_image_required(self):
        with self.assertRaisesRegexp(InvalidConfiguration, "ROOT_IMAGE option is not set"):
            self.environment.config.check()
    def test__configuration_defaults(self):
        self.environment.config.load_from_string('ROOT_IMAGE="a"')
        self.assertEquals(self.environment.config["INCLUDES"], [])
        self.assertEquals(self.environment.config["ENVIRON"], {})
    def test__getitem_setitem(self):
        self.environment.config["ROOT_IMAGE"] = "a"
        self.assertEquals(self.environment.config["ROOT_IMAGE"], "a")
    def test__unknown_configuration(self):
        with self.assertRaises(UnknownConfigurationOptions):
            self.environment.config.load_from_string("ROOT_IMAGE='a'\nA=2")
        with self.assertRaises(UnknownConfigurationOptions):
            self.environment.config["A"] = 2
    def test__user_config_file(self):
        path = os.path.join(mkdtemp(), "subdir", "config.py")
        self.environment.config["ROOT_IMAGE"] = "bla" # to make check() work later
        self.assertFalse(os.path.exists(path))
        self.assertFalse(os.path.exists(os.path.dirname(path)))
        self.environment.config.process_user_config_file(path)
        self.assertTrue(os.path.isfile(path))
        self.environment.config.check()
        self.assertGreater(os.path.getsize(path), 0)
    def test__configuration_state(self):
        first_config = """
ROOT_IMAGE = "a"
INCLUDES = [Include("/a", "/x")]
        """
        second_config = """
ROOT_IMAGE = "b"
INCLUDES += [Include("/b", "/x")]
        """
        self.environment.config.load_from_string(first_config)
        self.environment.config.load_from_string(second_config)
        self.assertEquals(self.environment.config["ROOT_IMAGE"], "b")
        self.assertEquals([include.dest for include in self.environment.config["INCLUDES"]],
                          ["/a", "/b"])
        
    
