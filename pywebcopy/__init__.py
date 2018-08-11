# -*- coding: utf-8 -*-

"""
aerwebcopy
~~~~~~~~~~

A pythonic library to mirror any online website as is.
It respects robots.txt

"""


import core
import structures
import config
import utils
import generators
import exceptions
import test_generators

__version__ = config.config['version']
__author__ = 'Raja Tomar'
__copyright__ = 'Copyright Aeroson Systems & Co.'
__license__ = 'Licensed under MIT'
__email__ = 'rajatomar788@gmail.com'


__all__ = [
    '__version__', '__author__', '__copyright__', '__license__', '__email__',
    'core', 'structures', 'config', 'utils', 'generators', 'exceptions'
]


