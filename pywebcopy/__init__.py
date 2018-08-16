# -*- coding: utf-8 -*-

"""
aerwebcopy
~~~~~~~~~~

A pythonic library to mirror any online website as is.
It respects robots.txt

"""

import sys
import core
import structures
import config
import utils
import generators
import exceptions


__version__ = config.config['version']
__author__ = 'Raja Tomar'
__copyright__ = 'Copyright Aeroson Systems & Co.'
__license__ = 'Licensed under MIT'
__email__ = 'rajatomar788@gmail.com'


__all__ = [
    '__version__', '__author__', '__copyright__', '__license__', '__email__',
    'core', 'structures', 'config', 'utils', 'generators', 'exceptions'
]


if __name__ == '__main__':
    core.save_webpage(
        url='https://google.com/',
        mirrors_dir="E:\\Programming\\Projects\\WebsiteCopier\\archive\\\Mirrors_dir",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        copy_all=False,
        over_write=True,
        bypass_robots=True,
    )
