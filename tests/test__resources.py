from .test_utils import TestCase
from dwight_chroot import resources

class ResourceTypeDetectionTest(TestCase):
    def test__local_resource(self):
        self.assertDetectedAs("/a/b/c", resources.LocalResource)
    def test__git_resource(self):
        self.assertDetectedAs("git://git_server/repo", resources.GitResource)
    def test__web_resource(self):
        self.assertDetectedAs("http://server/file.tar.gz", resources.HTTPResource)
        self.assertDetectedAs("https://secure_server/file.tar.gz", resources.HTTPResource)
    def assertDetectedAs(self, string, resource_type):
        self.assertIs(resource_type, resources.Resource.get_resource_type_from_string(string))
