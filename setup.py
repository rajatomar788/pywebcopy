# Copyright 2019; Raja Tomar
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install wheel
#   $ pip install twine

import io
import os
import sys
from shutil import rmtree

from setuptools import setup
from setuptools import Command

from pywebcopy import __version__

# Package meta-data.
NAME = __version__.__title__
DESCRIPTION = __version__.__description__
URL = __version__.__url__
LICENSE = __version__.__license__
EMAIL = __version__.__email__
AUTHOR = __version__.__author__
VERSION = __version__.__version__

# What packages are required for this module to be executed?
REQUIRED = []


# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'requirements.txt')) as r:
    for rq in r.readlines():
        REQUIRED.append(rq.strip("\n"))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[1m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        #self.status("Setting up git..")
        #os.system('git init')
        #os.system('git add .')

        #self.status("Pushing to github master branch..")
        #os.system('git push origin master')

        #self.status('Publishing git tags…')
        #os.system('git tag v{0}'.format(VERSION))
        #os.system('git push origin --tags')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    # If your package is a single module, use py_modules instead of 'packages':
    packages=[__version__.__title__],

    install_requires=REQUIRED,
    include_package_data=True,
    license=LICENSE,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: %s' % LICENSE,
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
