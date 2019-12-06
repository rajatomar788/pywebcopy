# encoding: utf8
"""

pywebcopy
~~~~~~~~~

Command line usage provider for pywebcopy.

.. version changed :: 6.0.0
    1. Replaced old manual command processing with `Fire` library.
    2. Added default command-line config
        a. `bypass_robots` = True

.. version changed :: 6.1.0
    1. Added command `version` which prints current version
    2. FIX: Tests were not running due to bad path detection

"""

import os
import sys

import fire

from pywebcopy import (
    __version__ as ver,
    save_webpage as swp,
    save_website as sws,
)


class Commands(object):
    # Defaults to the file documentation
    __doc__ = __doc__

    def __repr__(self):
        return 'Default command-line interface'

    # Command-line configuration has some defaults
    __config__ = {
        'bypass_robots': True,
    }
    __tests__ = os.path.join(os.path.dirname(__name__), 'tests')

    def save_webpage(self, *args, **kwargs):
        kwargs.update(self.__config__)
        return swp(*args, **kwargs)

    def save_website(self, *args, **kwargs):
        kwargs.update(self.__config__)
        return sws(*args, **kwargs)

    @staticmethod
    def version():
        sys.stdout.write(ver)

    def run_tests(self):
        """
        Runs tests if available.
        """
        if os.path.exists(self.__tests__):
            os.system('{0} -m unittest {1}'.format(sys.executable, self.__tests__))
        else:
            sys.stdout.write('-' * 70)
            sys.stdout.write('\nNo tests found! Try downloading the package from github!')
            sys.stdout.flush()


fire.Fire(Commands)
