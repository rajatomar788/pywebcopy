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


__version__ = config.config['version']
__author__ = 'Raja Tomar'
__copyright__ = 'Copyright Aeroson Systems & Co.'
__license__ = 'Licensed under MIT'
__email__ = 'rajatomar788@gmail.com'


__all__ = [
    '__version__', '__author__', '__copyright__', '__license__', '__email__',
    'core', 'structures', 'config', 'utils', 'generators'
]

if __name__ == "__main__":
    import os
    core.init("https://google.com", mirrors_dir=os.path.join("E:\Programming\Projects\WebsiteCopier\\", "Mirrors_dir"), bypass_robots=True, over_write=True)