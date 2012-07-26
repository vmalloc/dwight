from .test_utils import TestCase
import functools
import itertools
from dwight_chroot import resources
from dwight_chroot.exceptions import UsageException

class ResourceTypeDetectionTest(TestCase):
    def test__local_resource(self):
        self.assertDetectedAs("/a/b/c", resources.LocalResource)
    def test__git_resource(self):
        self.assertDetectedAs("git://git_server/repo", resources.GitResource)
        self.assertDetectedAs("ssh+git://git_server/repo", resources.GitResource)
    def test__hg_resource(self):
        self.assertDetectedAs("http+hg://server/repo", resources.MercurialResource)
        self.assertDetectedAs("https+hg://server/repo", resources.MercurialResource)
    def test__web_resource(self):
        self.assertDetectedAs("http://server/file.tar.gz", resources.HTTPResource)
        self.assertDetectedAs("https://secure_server/file.tar.gz", resources.HTTPResource)
    def assertDetectedAs(self, string, resource_type):
        self.assertIs(resource_type, resources.Resource.get_resource_type_from_string(string))

class DVCSResourceTest(TestCase):
    def test__cannot_specify_multiple_checkout_options(self):
        for url in ("git://a/b", "http+hg://a/b"):
            resource_type = resources.Resource.get_resource_type_from_string(url)
            for branch, tag, commit in itertools.product([None, "a"], [None, "b"], [None, "c"]):
                r = functools.partial(resource_type, url, branch=branch, tag=tag, commit=commit)
                if len(set([branch, tag, commit]) - set([None])) <= 1:
                    r()
                else:
                    with self.assertRaises(UsageException):
                        r()
