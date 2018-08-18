# -*- coding: utf-8 -*-

"""
aerwebcopy.exceptions
~~~~~~~~~~~~~~~

Exceptions which can occur in aerwebcopy engine.
"""


class PywebcopyException(IOError):
    """ Base class for other exceptions which are defined. """
    def __init__(self, *args, **kwargs):
        super(PywebcopyException, self).__init__(*args, **kwargs)


class AccessError(PywebcopyException):
    """ Access to resource not allowed. """


class InvalidUrl(PywebcopyException):
    """ Supplied url is not a valid URL. """


class InvalidFilename(PywebcopyException):
    """ Filename is either too long or contains special characters 
    which are not supported by filesystem. """


class UndefinedConfigValue(PywebcopyException):
    """ If a specific configuration value is set to None """


class ConnectError(PywebcopyException):
    """ Internet connection is not found. """
    
