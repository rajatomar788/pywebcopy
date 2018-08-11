# -*- coding: utf-8 -*-

"""
aerwebcopy.config
~~~~~~~~~~~~~~~~~

Configuration modifying aerwebcopy.
"""

import re
import structures


__all__ = [
    'config', 'update_config', 'reset_config'
]

# --------------------------------------------------
# DO NOT MODIFY, you can change these through update_config()
# --------------------------------------------------
config = structures.CaseInsensitiveDict({
    # version no. of this build
    'VERSION': '2.0beta',
    # not so helpful debug switch, it just dumps the log
    # on the console
    'DEBUG': False,
    # make zip archive of the downloaded content
    'MAKE_ARCHIVE': True,
    # delete the project folder after making zip archive of it
    'CLEAN_UP': False,
    # to download css file or not
    'LOAD_CSS': True,
    # to download images or not
    'LOAD_IMAGES': True,
    # to download js file or not
    'LOAD_JAVASCRIPT': True,
    # to download every page available inside url tree turn this True
    'COPY_ALL': False,
    # to overwrite the existing files if found
    'OVER_WRITE': False,
    # allowed file extensions
    'ALLOWED_FILE_EXT': ['.html', '.php', '.asp', '.htm', '.xhtml', '.css', 
                        '.json', '.js', '.xml', '.svg', '.gif', '.ico', '.jpeg',
                         '.jpg', '.png', '.ttf', '.eot', '.otf', '.woff'],
    # log file path
    'LOG_FILE': None,
    # reduce log produced by removing unnecessary info from log file
    'LOG_FILE_COMPRESSION': False,
    # log buffering store log in ram until finished, then write to file
    'LOG_BUFFERING': False,
    # log buffer holder for performance speed up
    'LOG_BUFFER_ARRAY': list(),
    # this pattern is used to validate file names
    'FILENAME_VALIDATION_PATTERN': re.compile(r'[*":<>\|\?]+'),
    # name of the mirror project
    'PROJECT_NAME': None,
    # url to download html page
    'URL': None,
    # define the base directory to store all copied sites data
    'MIRRORS_DIR': None,
    # all downloaded file location
    'DOWNLOADED_FILES': list(),
    # downloaded files size
    'DOWNLOAD_SIZE': 0
})


# HANDLE WITH CARE
config['USER_AGENT'] = 'Mozilla/5.0 (compatible; PywebcopyBot/{})'.format(config['version'])
config['ROBOTS'] = structures.RobotsTxt()
config['BYPASS_ROBOTS'] = False


""" This is used in to store default config as backup """
default_config = config


def update_config(**kwargs):
    """ Updates the default `config` dict """
    config.update(**kwargs)


def reset_config():
    """ Resets all to configuration to default state. """
    global config
    config = default_config

