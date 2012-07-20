from .test_utils import EnvironmentTestCase
from dwight_chroot.exceptions import (
    CannotLoadConfiguration,
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
    
