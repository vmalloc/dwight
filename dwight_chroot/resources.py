import functools
import os
import shutil
import six

if six.PY3:
    import urllib as urllib2
    from urllib.parse import urlsplit
else:
    import urllib2
    from urlparse import urlsplit
from .exceptions import UsageException
from .platform_utils import execute_command_assert_success

class Resource(object):
    @classmethod
    def get_resource_type_from_string(cls, s):
        if s.startswith("git://") or s.startswith("ssh+git://"):
            return GitResource
        if s.startswith("http+hg://") or s.startswith("https+hg://"):
            return MercurialResource
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

class DVCSResource(CacheableResource):
    def __init__(self, repo_url, commit=None, branch=None):
        super(DVCSResource, self).__init__()
        self.repo_url = repo_url
        if commit is not None and branch is not None:
            raise UsageException("Cannot specify both branch and commit for git resources")
        self.commit = commit
        self.branch = branch
    def get_cache_key(self):
        return dict(url=self.repo_url, commit=self.commit, branch=self.branch)
    def fetch(self, path):
        self._refresh(path, initialize=True)
    def refresh(self, path):
        self._refresh(path, initialize=False)
    def _refresh(self, path, initialize):
        if initialize:
            shutil.rmtree(path)
            self._clone_into(path)
            if self.commit:
                # a commit never changes, so we only do this upon
                # initialization
                self._checkout_commit(path)
            if self.branch:
                self._checkout_branch(path)
        elif not self.commit:
            self._pull_changes(path)

class MercurialResource(DVCSResource):
    def __init__(self, *args, **kwargs):
        super(MercurialResource, self).__init__(*args, **kwargs)
        self._fix_url_scheme()
    def _fix_url_scheme(self):
        for prefix, fix in [
                ("http+hg://", "http://"),
                ("https+hg://", "https://")
        ]:
            if self.repo_url.startswith(prefix):
                self.repo_url = fix + self.repo_url[len(prefix):]
                break
    def _clone_into(self, path):
        cmd = "hg clone"
        if self.commit:
            cmd += " -r {0}".format(self.commit)
        if self.branch:
            cmd += " -b {0}".format(self.branch)
        cmd += " {0} {1}".format(self.repo_url, path)
        execute_command_assert_success(cmd)
    def _checkout_branch(self, path):
        pass
    def _checkout_commit(self, path):
        pass
    def _pull_changes(self, path):
        if not self.commit:
            execute_command_assert_success("hg pull", cwd=path)

class GitResource(DVCSResource):
    def _clone_into(self, path):
        execute_command_assert_success("git clone {0} {1}".format(self.repo_url, path))
    def _checkout_branch(self, path):
        assert self.branch
        execute_command_assert_success(
            "git fetch origin && git checkout -b {0} origin/{0}".format(self.branch),
            cwd=path)
    def _checkout_commit(self, path):
        assert self.commit
        execute_command_assert_success(
            "git fetch origin && git checkout {0} && git reset --hard".format(self.commit),
            cwd=path
            )
    def _pull_changes(self, path):
        execute_command_assert_success(
            "git pull",
            cwd=path
            )

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
        _, _, path, _, _ = urlsplit(url)
        name = path.split("/")[-1]
        if not name:
            name = "file"
        return name
