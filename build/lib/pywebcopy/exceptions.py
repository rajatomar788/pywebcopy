# -*- coding: utf-8 -*-

"""
pywebcopy.exceptions
~~~~~~~~~~~~~~~~~~~~

Exceptions which can occur in pywebcopy.
"""


class PywebcopyError(IOError):
    """Base class for any Error generated through package. """
    def __init__(self, *args, **kwargs):
        super(PywebcopyError, self).__init__(*args, **kwargs)


class InvalidUrlError(PywebcopyError, ValueError):
    """Provided url doesn't seems to work."""


class InvalidPathError(PywebcopyError, ValueError):
    """Provided path is invalid in creating paths on file system. """


class ConnectionError(PywebcopyError):
    """Connection to the server couldn't be established either due to server
    error or http error. """


class AccessError(PywebcopyError):
    """Requested url is flagged private by the Site owner."""


class RequiredAttributesMissing(PywebcopyError):
    """You have called a class or function without setting up environment or attributes."""
