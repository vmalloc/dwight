from contextlib import contextmanager
import itertools
import json
import logging
import os
import shutil

from . import resources

_logger = logging.getLogger(__name__)

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
                return existing_item["path"]
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
            key=key, path=path, size=self._get_path_total_size(path)
            ))
        self._save_state_to_file()
    def _get_path_total_size(self, path):
        return sum(os.path.getsize(os.path.join(p, filename)) 
                   for p, _, filenames in os.walk(path)
                   for filename in filenames)
    def update_path(self, path):
        for item in self._state["items"]:
            if item["path"] == path:
                item["size"] = self._get_path_total_size(path)
                break
        else:
            raise LookupError("{0} not found in cache state".format(path))
    def cleanup(self, max_size, skip_keys):
        current_size = sum(item["size"] for item in self._state["items"])
        to_remove = []
        for index, item in enumerate(self._state["items"]):
            if current_size <= max_size:
                break
            if item["key"] not in skip_keys:
                item_size = item["size"]
                current_size -= item_size
                to_remove.append((index, item))
        try:
            for index, item in reversed(to_remove):
                _logger.debug("Purging cache item %r", item["key"])
                path = item["path"]
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)
                self._state["items"].pop(index)
        finally:
            self._save_state_to_file()
            
        

