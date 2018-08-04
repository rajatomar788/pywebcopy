# -*- coding: utf-8 -*-

"""
aerwebcopy.config
~~~~~~~~~~~~~~~~~

Configuration modifying aerwebcopy.
"""

import re
import structures


__all__ = [
    'config'
]

# --------------------------------------------------
# DO NOT MODIFY, you can change these through init()
# --------------------------------------------------
config = structures.CaseInsensitiveDict({

    'VERSION': '1.9.2',

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
    'ALLOWED_FILE_EXT': ['.html', '.php', '.asp', '.htm', '.xhtml', '.css', '.json', '.js', '.xml', '.svg', '.gif', '.ico', '.jpeg',
                         '.jpg', '.png', '.ttf', '.eot', '.otf', '.woff'],
    # file to write all valid links found on pages
    'LINK_INDEX_FILE': None,
    # log file path
    'LOG_FILE': None,
    # reduce log produced by removing unnecessary info from log file
    'LOG_FILE_COMPRESSION': False,
    # log buffering store log in ram until finished, then write to file
    'LOG_BUFFERING': True,
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

# user agent to be shown on requests made to server
config['USER_AGENT'] = 'Mozilla/4.0 (compatible; WebCopyBot/{};  +Non-Harmful-LightWeight)'.format(config['version'])

# HANDLE WITH CARE
config['BYPASS_ROBOTS'] = False
