# -*- coding: utf-8 -*-

"""
pywebcopy
~~~~~~~~~

Python library to copy webpages.
"""
<<<<<<< HEAD
'''
__all__ = [
    'VERSION', 'LOGGER', 'SESSION',
    'exceptions', 'utils',
    'config', 'Url', 'filename_present', 'url2path',
    'Asset', 'LinkTag', 'ScriptTag', 'ImgTag',
    'parse', 'parse_content',
    'get', 'new_file',
    'AssetsGenerator',
    'WebPage', 'Crawler',
    'save_webpage', 'save_website',
]
'''
=======

__all__ = [
    'VERSION', 'LOGGER', 'SESSION',
    'utils',
    'config', 'URLTransformer', 'filename_present', 'url2path',
    'FileMixin', 'LinkTag', 'ScriptTag', 'ImgTag',
    'parse', 'parse_content',
    'get', 'new_file',
    'WebPage', 'Crawler',
    'save_webpage', 'save_website',
]

>>>>>>> v5.0.0
__author__ = 'Raja Tomar'
__email__ = 'rajatomar788@gmail.com'
__license__ = 'MIT License'

<<<<<<< HEAD
import requests
import logging

DEBUG = False

VERSION = '4.0.1'
__version__ = VERSION   # alias


# Global Logger object for use in modules
LOGGER = logging.getLogger("pywebcopy")
LOGGER.setLevel(logging.DEBUG)

# Log entry formatter
_l_fmt = logging.Formatter("%(created)s - %(levelname)s - %(name)s.%(module)s.%(funcName)s:%(lineno)d - %(message)s")

# Log entry datetime _l_fmt
_l_fmt.datefmt = "%d-%b-%Y %H:%M:%S"


def _n_consoleLogger():
    c_logger = logging.StreamHandler()
    c_logger.setLevel(logging.INFO)
    c_logger.setFormatter(_l_fmt)
    return c_logger


def _n_fileLogger(file_path, mode):
    f_logger = logging.FileHandler(file_path, mode)
    f_logger.setLevel(logging.DEBUG)
    f_logger.setFormatter(_l_fmt)
    return f_logger


LOGGER.addHandler(_n_consoleLogger())


"""Global `requests` session object to store cookies in subsequent http requests """
SESSION = requests.Session()


from pywebcopy import exceptions
from pywebcopy import utils
from pywebcopy.config import config
from pywebcopy.urls import Url, filename_present, url2path
from pywebcopy.elements import Asset, LinkTag, ScriptTag, ImgTag
from pywebcopy.parsers import parse, parse_content, WebPage, BaseParser
from pywebcopy.generators import AssetsGenerator
from pywebcopy.core import get, new_file
from pywebcopy.workers import Crawler, save_website, save_webpage
=======
import sys

this = sys.modules[__name__]
this.DEBUG = False
DEBUG = this.DEBUG
VERSION = 'v5.0.0'

from .logger import LOGGER  # Global Logger instance


import requests
SESSION = requests.Session()
SESSION.__doc__ = """Global `requests` session object to store cookies in subsequent http requests."""


from . import utils
from .configs import config
from .urls import URLTransformer, filename_present, url2path
from .elements import FileMixin, LinkTag, ScriptTag, ImgTag
from .parsers import parse, parse_content, BaseParser, Element
from .webpage import WebPage, ElementsHandler, save_webpage
from .core import get, new_file
from .crawler import Crawler, save_website
>>>>>>> v5.0.0

