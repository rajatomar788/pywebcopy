# encoding: utf8
"""

pywebcopy
~~~~~~~~~

Command line usage provider for pywebcopy.

.. version changed :: 6.0.1
    1. Replaced old manual command processing with `Fire` library.
    2. Added default command-line config
        a. `bypass_robots` = True

"""

import os
import sys

import fire

from pywebcopy import (
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

    def save_webpage(self, *args, **kwargs):
        kwargs.update(self.__config__)
        return swp(*args, **kwargs)

    def save_website(self, *args, **kwargs):
        kwargs.update(self.__config__)
        return sws(*args, **kwargs)

    @staticmethod
    def run_tests():
        """
        Runs tests if available.
        """
        tests_dir = 'tests'
        tests_dir_abs = os.path.join(os.getcwd(), tests_dir)

        if os.path.exists(tests_dir_abs):
            os.system('{} -m unittest {}'.format(sys.executable, tests_dir))
        else:
            sys.stdout.write('-' * 70)
            sys.stdout.write('\nNo tests found! Try downloading the package from github!')
            sys.stdout.flush()


fire.Fire(Commands)
