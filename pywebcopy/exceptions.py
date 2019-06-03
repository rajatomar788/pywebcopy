# -*- coding: utf-8 -*-

"""
pywebcopy.exceptions
~~~~~~~~~~~~~~~~~~~~

Exceptions which can occur in pywebcopy.
"""


class PywebcopyError(IOError):
    """Pywebcopy has come across an error which could be safe or critical."""
    def __init__(self, *args):
        IOError.__init__(self, *args)


class InvalidUrlError(PywebcopyError, ValueError):
    """Provided url doesn't seems to work."""


class InvalidPathError(PywebcopyError, ValueError):
    """Provided path is invalid in creating paths on file system. """


class ConnectError(PywebcopyError):
    """Connection to the server couldn't be established either due to server
    error or http error. """


class AccessError(PywebcopyError):
    """Requested url is flagged private by the Site owner."""


class ParseError(PywebcopyError, RuntimeError):
    """Runtime error occurred during the parsing of html."""


class UrlRefusedByTagHandlerError(PywebcopyError):
    """Url has been rejected by the verification provider of the Tag handler."""


class UrlTransformerNotSetup(PywebcopyError, UnboundLocalError):
    """UrlTransformer method is not subclass and not being made available."""


class RequiredAttributesMissing(PywebcopyError):
    """You have called a class or function without setting up environment or attributes."""
