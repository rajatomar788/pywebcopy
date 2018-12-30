# -*- coding: utf-8 -*-

"""
pywebcopy
~~~~~~~~~

Python library to copy webpages.
"""

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

__author__ = 'Raja Tomar'
__email__ = 'rajatomar788@gmail.com'
__license__ = 'MIT License'

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

