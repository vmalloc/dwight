from .test_utils import EnvironmentTestCase
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
    
