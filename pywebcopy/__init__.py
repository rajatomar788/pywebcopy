# -*- coding: utf-8 -*-
"""
pywebcopy
~~~~~~~~~

Python library to clone complete webpages and websites.


Copyright 2019 Raja Tomar

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""


__author__ = 'Raja Tomar'
__email__ = 'rajatomar788@gmail.com'
__license__ = 'Apache License 2.0'
__version__ = (6, 0, 0, 'beta', 0)


from .globals import *
from .logger import LOGGER  # Global Logger instance
from .configs import config, SESSION
from .urls import URLTransformer, filename_present
from .elements import LinkTag, ScriptTag, ImgTag, AnchorTag, TagBase
from .webpage import WebPage
from .core import get, new_file
from .crawler import Crawler
from .api import save_website, save_webpage


__all__ = [
    'save_webpage', 'save_website',                             #: apis
    'config',                                                   #: configuration
    'WebPage', 'Crawler',                                       #: Classes
    'SESSION',                                                  #: Http Session
    'URLTransformer', 'filename_present',                       #: Url manipulation
    'TagBase', 'LinkTag', 'ScriptTag', 'ImgTag', 'AnchorTag',   #: Customisable tag handling
    'get', 'new_file',                                          #: some goodies
]


def __dir__():
    return __all__ + [__version__, __author__, __email__, __license__]
