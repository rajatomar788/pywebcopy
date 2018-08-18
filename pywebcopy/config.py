# -*- coding: utf-8 -*-

"""
aerwebcopy.config
~~~~~~~~~~~~~~~~~

* DO NOT MODIFY *

Configuration modifying aerwebcopy.
"""


import os
import re
core = __import__('core')
utils = __import__('utils')
structures = __import__('structures')
exceptions = __import__('exceptions')



global version
version = '2.0.0'


config = structures.CaseInsensitiveDict({

    # version no. of this build
    'VERSION': version,
    # not so helpful debug switch, it just dumps the log
    # on the console
    'DEBUG': False,
    # make zip archive of the downloaded content
    'MAKE_ARCHIVE': True,
    # delete the project folder after making zip archive of it
    'CLEAN_UP': False,
    # parser for parsing html pages
    'PARSER': 'lxml',
    # to download css file or not
    'LOAD_CSS': True,
    # to download images or not
    'LOAD_IMAGES': True,
    # to download js file or not
    'LOAD_JAVASCRIPT': True,
    # to overwrite the existing files if found
    'OVER_WRITE': False,
    # allowed file extensions
    'ALLOWED_FILE_EXT': ['.html', '.php', '.asp', '.htm', '.xhtml', '.css',
                         '.json', '.js', '.xml', '.svg', '.gif', '.ico', '.jpeg', '.pdf',
                         '.jpg', '.png', '.ttf', '.eot', '.otf', '.woff', '.woff2',],

    # Completely silents the script except 'trace' functions in debug mode
    'QUIET' : False,
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
    'DOWNLOAD_SIZE': 0,

    # HANDLE WITH CARE

    # to download every page available inside url tree turn this True
    'COPY_ALL': False,
    # user-agent of this scripts requests
    'USER_AGENT' : 'Mozilla/5.0 (PywebcopyBot/{})'.format(version),
    # dummy robots.txt class
    'ROBOTS' : structures.RobotsTxt(''),
    # bypass sites policy
    'BYPASS_ROBOTS' : False
})


""" This is used in to store default config as backup """
default_config = dict(config)


def update_config(**kwargs):
    """ Updates the default `config` dict """
    config.update(**kwargs)


def reset_config():
    """ Resets all to configuration to default state. """
    global config
    config = structures.CaseInsensitiveDict(default_config)



def setup_config(url, download_loc, **kwargs):
    """ Easiest way to auto configure config keys for error free usage.
    Just provide the params and every other config key is automatically
    configured.

    :param url: url of the page to work with
    :param download_loc: path where to store the downloaded content
    """


    # check if the provided url works
    _dummy_request = core.get(url)

    # new resolved url
    _url = _dummy_request.url

    if not _dummy_request.ok:
        raise exceptions.ConnectionError("Provided URL '%s' didn't work!" % url)

    # Assign the resolved or found url so that it does not generate
    # error of redirection request
    config['URL'] = _url

    # if external configuration is provided then use it
    config.update(kwargs)

    if config['project_name'] is None:
        config['project_name'] = utils.hostname(_url)

    if config['mirrors_dir'] is None:
        config['mirrors_dir'] = os.path.abspath(
            os.path.join(download_loc, 'WebCopyProjects', config['project_name']
            ))

    if config['log_file'] is None:
        config['log_file'] = os.path.join(
            config['mirrors_dir'], config['project_name'] + '_log.log')

    # initialise the new robots parser so that we don't overrun websites
    # with copyright policies
    config['ROBOTS'] = structures.RobotsTxt(_url + '/robots.txt')

    # create work dirs if it do not exists
    if not os.path.exists(config['mirrors_dir']):
        os.makedirs(config['mirrors_dir'])

    # delete all the log in logfile and start afresh
    if os.path.isfile(config['log_file']):
        os.remove(config['log_file'])

    core.now(
        "Initialising the Script with following Configuration Set: \n\n%s" % dict(config),
        level=2,
        compressed=False
    )