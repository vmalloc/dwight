class DwightException(Exception):
    pass

class CommandFailed(DwightException):
    pass

class UsageException(DwightException):
    pass

class NotRootException(UsageException):
    pass

class ConfigurationException(DwightException):
    pass

class CannotLoadConfiguration(ConfigurationException):
    pass

class InvalidConfiguration(ConfigurationException):
    pass

class UnknownConfigurationOptions(ConfigurationException):
    pass

class RuntimeDwightException(DwightException):
    pass

class CannotMountPath(RuntimeDwightException):
    pass
