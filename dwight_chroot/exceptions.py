class DwightException(Exception):
    pass

class ConfigurationException(DwightException):
    pass

class CannotLoadConfiguration(ConfigurationException):
    pass

class InvalidConfiguration(ConfigurationException):
    pass

class UnknownConfigurationOptions(ConfigurationException):
    pass

