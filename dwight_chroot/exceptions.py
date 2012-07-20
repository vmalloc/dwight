class DwightException(Exception):
    pass

class ConfigurationException(DwightException):
    pass

class CannotLoadConfiguration(ConfigurationException):
    pass
