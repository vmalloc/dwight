class Resource(object):
    @classmethod
    def get_resource_type_from_string(cls, s):
        if s.startswith("git://"):
            return GitResource
        if s.startswith("http://") or s.startswith("https://"):
            return HTTPResource
        return LocalResource

class LocalResource(Resource):
    def __init__(self, path):
        super(LocalResource, self).__init__()
        self._path = path
    def get_path(self):
        return self._path

class FetchedResource(Resource):
    def get(self, path):
        raise NotImplementedError() # pragma: no cover

class CacheableResource(FetchedResource):
    def get_cache_key(self):
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
