import os
from .resources import Resource

class Include(object):
    def __init__(self, dest, source, **kwargs):
        super(Include, self).__init__()
        self.dest = os.path.abspath(dest)
        self.source = source
        self.kwargs = kwargs
    def to_resource(self):
        return Resource.get_resource_type_from_string(self.source)(self.source, **self.kwargs)
    def __repr__(self):
        return self.source
