import copy
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
    def fetch(self, path):
        shutil.rmtree(path)
        shutil.copytree(self.src_path, path)

class DummyEnvironment(object):
    def __init__(self):
        super(DummyEnvironment, self).__init__()
        self.cache = Cache(mkdtemp())
        
class CacheTest(TestCase):
    def setUp(self):
        super(CacheTest, self).setUp()
        self.env = DummyEnvironment()
        self.src_path = mkdtemp()
        with open(os.path.join(self.src_path, "somefile.txt"), "w") as f:
            f.write("hello")
        self.item = DummyCachedItem(dict(a=1, b="some_attr"), self.src_path)
    def test__fetching_from_scratch(self):
        path = self.item.get_path(self.env)
        self.assertTrue(os.path.isdir(path))
        for filename in os.listdir(path):
            self.assertIn(filename, os.listdir(self.src_path))
        return path
    def test__refreshing(self):
        old_path = self.test__fetching_from_scratch()
        self.assertEquals(self.item.refresh_count, 0)
        new_path = self.item.get_path(self.env)
        self.assertEquals(self.item.refresh_count, 1)
        self.assertEquals(new_path, old_path)
    def test__saving_and_reloading(self):
        path = self.test__fetching_from_scratch()
        old_state = copy.deepcopy(self.env.cache._state)
        self.env.cache = Cache(self.env.cache.root)
        self.assertEquals(self.env.cache._state, old_state)
    def test__new_item_on_already_existing_directory(self):
        os.makedirs(os.path.join(self.env.cache.root, "items", "0"))
        self.assertEquals(self.env.cache.create_new_path(), os.path.join(self.env.cache.root, "items", "1"))
