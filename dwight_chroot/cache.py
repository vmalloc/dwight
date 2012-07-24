import itertools
import os
import json

from . import resources

_STATE_FILE_NAME = ".state.json"

class Cache(object):
    def __init__(self, path):
        super(Cache, self).__init__()
        self.root = path
        self._state_file_path = os.path.join(self.root, _STATE_FILE_NAME)
        self._load_state()
    def _load_state(self):
        if os.path.exists(self._state_file_path):
            self._load_state_from_file()
        else:
            self._load_new_state()
    def _load_state_from_file(self):
        with open(self._state_file_path) as state_file:
            self._state = json.loads(state_file.read())
    def _save_state_to_file(self):
        with open(self._state_file_path, "w") as state_file:
            state_file.write(json.dumps(self._state))
    def _load_new_state(self):
        self._state = dict(items = [], next_id=0)
    def get_path(self, key):
        for existing_item in self._state["items"]:
            if existing_item["key"] == key:
                return  existing_item["path"]
        return None
    def create_new_path(self):
        while True:
            item_id = self._state["next_id"]
            self._state["next_id"] += 1
            path = os.path.join(self.root, "items", str(item_id))
            if not os.path.exists(path):
                break
        os.makedirs(path)
        return path
    def register_new_path(self, path, key):
        self._state["items"].append(dict(
            key=key, path=path
            ))
        self._save_state_to_file()

