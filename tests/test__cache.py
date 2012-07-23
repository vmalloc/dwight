import os
import shutil
from tempfile import mkdtemp
from .test_utils import TestCase
from dwight_chroot.cache import Cache
from dwight_chroot.resources import CacheableResource

class DummyCachedItem(CacheableResource):
    def __init__(self, key, src_path):
        super(DummyCachedItem, self).__init__()
        self.key = key
        self.src_path = src_path
        self.refresh_count = 0
    def get_cache_key(self):
        return self.key
    def refresh(self, path):
        self.refresh_count += 1
    def get(self, path):
        shutil.rmtree(path)
        shutil.copytree(self.src_path, path)

class CacheTest(TestCase):
    def setUp(self):
        super(CacheTest, self).setUp()
        self.src_path = mkdtemp()
        with open(os.path.join(self.src_path, "somefile.txt"), "w") as f:
            f.write("hello")
        self.cache_root = os.path.join(mkdtemp(), ".cache")
        self.cache = Cache(mkdtemp())
        self.cached_item = DummyCachedItem(dict(a=1, b="some_attr"), self.src_path)
    def test__fetching_from_scratch(self):
        path = self.cache.ensure(self.cached_item)
        self.assertTrue(os.path.isdir(path))
        for filename in os.listdir(path):
            self.assertIn(filename, os.listdir(self.src_path))
        return path
    def test__refreshing(self):
        old_path = self.test__fetching_from_scratch()
        self.assertEquals(self.cached_item.refresh_count, 0)
        new_path = self.cache.ensure(self.cached_item)
        self.assertEquals(self.cached_item.refresh_count, 1)
        self.assertEquals(new_path, old_path)
