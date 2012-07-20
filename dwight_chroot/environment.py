from .exceptions import CannotLoadConfiguration
    
class Environment(object):
    def __init__(self):
        super(Environment, self).__init__()
    def load_configuration_file(self, filename):
        with open(filename, "r") as configuration_file:
            self.load_configuration_string(configuration_file.read())
    def load_configuration_string(self, s):
        d = {}
        try:
            exec(s, d)
        except Exception as e:
            raise CannotLoadConfiguration("Cannot load configuration ({0})".format(e))
