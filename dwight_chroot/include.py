from .resources import Resource

class Include(object):
    def __init__(self, source, **kwargs):
        super(Include, self).__init__()
        self.source = source
        self.kwargs = kwargs
    def to_resource(self):
        return Resource.get_resource_type_from_string(self.source)(self.source, **self.kwargs)
    def __repr__(self):
        return self.source
