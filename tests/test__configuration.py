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
                self.environment.load_configuration_string(bad_source_string)
    def test__base_image_required(self):
        with self.assertRaisesRegexp(InvalidConfiguration, "ROOT_IMAGE is missing"):
            self.environment.load_configuration_string("")
    def test__configuration_defaults(self):
        self.environment.load_configuration_string('ROOT_IMAGE="a"')
        self.assertEquals(self.environment.includes, [])
        self.assertEquals(self.environment.environ, {})
    def test__unknown_configuration(self):
        with self.assertRaises(UnknownConfigurationOptions):
            self.environment.load_configuration_string("ROOT_IMAGE='a'\nA=2")
    
