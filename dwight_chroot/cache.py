import itertools
import os
import json

from . import resources

class Cache(object):
    def __init__(self, path):
        super(Cache, self).__init__()
        self.root = path
        self._reset_state()
    def _reset_state(self):
        self._state = dict(
            items = [],
            )
        self._item_id_generator = itertools.count()
    def ensure(self, resource):
        key = resource.get_cache_key()
        for existing_item in self._state["items"]:
            if existing_item["key"] == key:
                resource.refresh(existing_item["path"])
                return  existing_item["path"]
        item_id = next(self._item_id_generator)
        path = os.path.join(self.root, "items", str(item_id))
        os.makedirs(path)
        resource.get(path)
        self._state["items"].append(dict(
            key=key, path=path, id=item_id
            ))
        return path

