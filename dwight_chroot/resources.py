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
        self.commit = commit
        self.branch = branch

class HTTPResource(CacheableResource):
    def __init__(self, url):
        super(HTTPResource, self).__init__()
        self.url = url
