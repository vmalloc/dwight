import string
from .exceptions import (
    CannotLoadConfiguration,
    InvalidConfiguration,
    UnknownConfigurationOptions,
    )
    
class Environment(object):
    def __init__(self):
        super(Environment, self).__init__()
        self.reset_configuration()
    def reset_configuration(self):
        self.base_image = None
        self.extras = []
        self.environ = {}
        self.bind_mounts = {}
    def load_configuration_file(self, filename):
        with open(filename, "r") as configuration_file:
            self.load_configuration_string(configuration_file.read())
    def load_configuration_string(self, s):
        d = {}
        try:
            exec(s, {}, d)
        except Exception as e:
            raise CannotLoadConfiguration("Cannot load configuration ({0})".format(e))
        self.reset_configuration()
        if "ROOT_IMAGE" not in d:
            raise InvalidConfiguration("ROOT_IMAGE is missing in configuration")
        self.base_image = d.pop("ROOT_IMAGE")
        
        self.extras = d.pop("EXTRAS", [])
        self.environ = d.pop("ENVIRON", {})
        self.bind_mounts = d.pop("BIND_MOUNTS", {})
        unknown_parameters = self._get_unknown_parameters(d)
        if unknown_parameters:
            raise UnknownConfigurationOptions("Unknown options: {0}".format(", ".join(d)))
    def _get_unknown_parameters(self, configuration_dict):
        return [key for key in configuration_dict if key.isupper()]
                
