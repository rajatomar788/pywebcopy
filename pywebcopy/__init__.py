# -*- coding: utf-8 -*-
#
# Copyright 2019 Raja Tomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""

pywebcopy
~~~~~~~~~

Python library to clone web-pages and websites with all its peripheral files.

.. version changed :: 6.0.0
    1. **Breaking Change** New command-line interface using `Python Fire` library.
    2. Implemented type checks and path normalising in the `config.setup_paths`.

"""
__author__ = 'Raja Tomar'
__email__ = 'rajatomar788@gmail.com'
__license__ = 'Apache License 2.0'
__version__ = '6.0.0'

import logging

from .configs import config, SESSION
from .parsers import Parser, MultiParser
from .webpage import WebPage
from .crawler import Crawler
from .api import save_website, save_webpage

__all__ = [
    'WebPage', 'Crawler',
    'save_webpage', 'save_website',
    'config', 'SESSION',
    'Parser', 'MultiParser',
]

#: optimisations
logging.logThreads = 0
logging.logProcesses = 0
logging._srcfile = None
c_handler = logging.StreamHandler()
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[c_handler],
    format='%(name)-10s - %(levelname)-8s - %(message)s'
)
c_handler.setLevel(logging.INFO)
