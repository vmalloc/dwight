import functools
import logging
import os
import shutil

from .python_compat import (
    urllib2,
    urlsplit,
    )

from .exceptions import UsageException
from .platform_utils import execute_command_assert_success

_logger = logging.getLogger(__name__)

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
            env.cache.update_path(path)
        return path
    def get_cache_key(self):
        raise NotImplementedError() # pragma: no cover
    def fetch(self, path):
        raise NotImplementedError() # pragma: no cover
    def refresh(self, path):
        raise NotImplementedError() # pragma: no cover

class DVCSResource(CacheableResource):
    def __init__(self, repo_url, commit=None, branch=None, tag=None):
        super(DVCSResource, self).__init__()
        self.repo_url = repo_url
        self.commit = commit
        self.branch = branch
        self.tag = tag
        self._check_parameters()
        self._needs_pull = (commit is None and tag is None)
    def _check_parameters(self):
        if len([x for x in (self.commit, self.branch, self.tag) if x is not None]) > 1:
            raise UsageException("Can only specify at most one of (commit/branch/tag) for SCM resources")
    def get_cache_key(self):
        return dict(url=self.repo_url, commit=self.commit, branch=self.branch, tag=self.tag)
    def fetch(self, path):
        shutil.rmtree(path)
        self._clone(path)
    def refresh(self, path):
        if self._needs_pull:
            self._pull(path)

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
    def _clone(self, path):
        cmd = "hg clone"
        if self.commit or self.tag:
            cmd += " -r {0}".format(self.commit or self.tag)
        if self.branch:
            cmd += " -b {0}".format(self.branch)
        cmd += " {0} {1}".format(self.repo_url, path)
        execute_command_assert_success(cmd, unsudo=True)
    def _pull(self, path):
        execute_command_assert_success("hg pull", cwd=path, unsudo=True)

class GitResource(DVCSResource):
    def _clone(self, path):
        execute_command_assert_success("git clone {0} {1}".format(self.repo_url, path), unsudo=True)
        if self.branch:
            execute_command_assert_success(
                "git checkout -b {0} origin/{0}".format(self.branch),
                cwd=path,
                unsudo=True,
                )
        if self.commit or self.tag:
            execute_command_assert_success(
                "git checkout {0}".format(self.commit or self.tag),
                cwd=path,
                unsudo=True,
                )
    def _pull(self, path):
        execute_command_assert_success(
            "git pull",
            cwd=path,
            unsudo=True,
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
        _logger.info("Fetching %s", self.url)
        with open(output_path, "w") as output_file:
            shutil.copyfileobj(urllib2.urlopen(self.url), output_file)
        return output_path
    def _deduce_output_file_name(self, url):
        _, _, path, _, _ = urlsplit(url)
        name = path.split("/")[-1]
        if not name:
            name = "file"
        return name
