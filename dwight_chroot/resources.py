import functools
import os
import shutil
import urllib2
import urlparse

from .exceptions import UsageException
from .platform_utils import execute_command_assert_success

class Resource(object):
    @classmethod
    def get_resource_type_from_string(cls, s):
        if s.startswith("git://") or s.startswith("ssh+git://"):
            return GitResource
        if s.startswith("http://") or s.startswith("https://"):
            return HTTPResource
        return LocalResource
    @classmethod
    def from_string(cls, s):
        return cls.get_resource_type_from_string(s)(s)
    def get_path(self, env):
        raise NotImplementedError() # pragma: no cover

class LocalResource(Resource):
    def __init__(self, path):
        super(LocalResource, self).__init__()
        self._path = path
    def get_path(self, env):
        return self._path

class FetchedResource(Resource):
    pass

class CacheableResource(FetchedResource):
    def get_path(self, env):
        key = self.get_cache_key()
        path = env.cache.get_path(key)
        if path is None:
            path = env.cache.create_new_path()
            fetch_result = self.fetch(path)
            if fetch_result:
                path = fetch_result
            env.cache.register_new_path(path, key)
        else:
            self.refresh(path)
        return path
    def get_cache_key(self):
        raise NotImplementedError() # pragma: no cover
    def fetch(self, path):
        raise NotImplementedError() # pragma: no cover
    def refresh(self, path):
        raise NotImplementedError() # pragma: no cover

class GitResource(CacheableResource):
    def __init__(self, repo_url, commit=None, branch=None):
        super(GitResource, self).__init__()
        self.repo_url = repo_url
        if commit is not None and branch is not None:
            raise UsageException("Cannot specify both branch and commit for git resources")
        if commit is None and branch is None:
            branch = "master"
        self.commit = commit
        self.branch = branch
    def get_cache_key(self):
        return dict(url=self.repo_url, commit=self.commit, branch=self.branch)
    def fetch(self, path):
        self._refresh(path, initialize=True)
    def refresh(self, path):
        self._refresh(path, initialize=False)
    def _refresh(self, path, initialize):
        execute = functools.partial(execute_command_assert_success, cwd=path)
        if initialize:
            shutil.rmtree(path)
            execute_command_assert_success("git clone {0} {1}".format(self.repo_url, path))
        else:
            execute("git fetch origin")
        if self.branch:
            execute("git fetch origin && git checkout origin/{0} && git reset --hard".format(self.branch))
        else:
            assert self.commit
            execute("git checkout {0} && git reset --hard".format(self.commit))
        

class HTTPResource(CacheableResource):
    def __init__(self, url):
        super(HTTPResource, self).__init__()
        self.url = url
        self._filename = self._deduce_output_file_name(url)
    def get_cache_key(self):
        return self.url
    def refresh(self, path):
        pass
    def fetch(self, path):
        output_path = os.path.join(path, self._filename)
        with open(output_path, "w") as output_file:
            shutil.copyfileobj(urllib2.urlopen(self.url), output_file)
        return output_path
    def _deduce_output_file_name(self, url):
        _, _, path, _, _ = urlparse.urlsplit(url)
        name = path.split("/")[-1]
        if not name:
            name = "file"
        return name
