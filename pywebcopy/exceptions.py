# -*- coding: utf-8 -*-

"""
aerwebcopy.exceptions
~~~~~~~~~~~~~~~

* DO NOT TOUCH *

Exceptions which can occur in aerwebcopy engine.
"""


class BaseError(Exception):
    """ Base class for other exceptions which are defined. """
    pass


class PermissionError(BaseError):
    """ Access to resource not allowed. """
    pass


class InvalidUrl(BaseError):
    """ Supplied url is not a valid URL. """
    pass


class InvalidFilename(BaseError):
    """ Filename is either too long or contains special characters 
    which are not supported by filesystem. """
    pass


class UndefinedConfigValue(BaseError):
    """ If a specific configuration value is set to None """
    pass


class ConnectionError(BaseError):
    """ Internet connection is not found. """
    pass


