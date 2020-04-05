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

Python library to clone web-pages and web-sites with all its peripheral files.

.. version changed :: 6.0.0
    1. **Breaking Change** New command-line interface using `Python Fire` library.
    2. **Breaking change** `WebPage` class now doesnt take any argument
    3. FIX: Implemented type checks and path normalising in the `config.setup_paths`.
    4. Added new dynamic `pywebcopy.__all__` attr generation.
    5. NEW: `WebPage` class has new methods `WebPage.get` and `WebPage.set_source`
    6. FIX: Queuing of downloads is replaced with a barrier to manage active threads

.. version changed :: 6.1.0
    1. FIX: url when refactored was sometimes different from actual file path generated.
    2. FIX: fixed path issue when using relative path for project_folder
    3. FIX: Some tests were not running due to bad path detection
    4. NEW: Added command `version` which prints current version

.. version changed :: 6.1.1
    1. FIX: Css linked files were not being recognised See issue #19
    2. FIX: Sometimes %22 was being appended to the url and response was error 403

"""

__author__ = 'Raja Tomar'
__email__ = 'rajatomar788@gmail.com'
__license__ = 'Apache License 2.0'
__version__ = '6.3.0'

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
    __author__, __email__,
    __license__, __version__,
]

#: logging optimisations
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
