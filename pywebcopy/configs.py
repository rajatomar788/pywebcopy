# -*- coding: utf-8 -*-

"""
pywebcopy.config
~~~~~~~~~~~~~~~~

Modifies the behaviour of pywebcopy.

"""


import os
import logging
from functools import lru_cache

import requests
from six.moves.urllib.parse import urlparse, urljoin

from . import LOGGER
from .globals import VERSION
from .exceptions import AccessError
from .logger import new_file_logger, new_html_logger, new_console_logger
from .structures import CaseInsensitiveDict, RobotsTxtParser


__all__ = ['default_config', 'config']


safe_file_exts = [
    '.html',
    '.php',
    '.asp',
    '.aspx',
    '.htm',
    '.xhtml',
    '.css',
    '.json',
    '.js',
    '.xml',
    '.svg',
    '.gif',
    '.ico',
    '.jpeg',
    '.pdf',
    '.jpg',
    '.png',
    '.ttf',
    '.eot',
    '.otf',
    '.woff',
    '.woff2',
    '.pwcf',  #: Default file extension
]

safe_http_headers = {
    "Accept-Language": "en-US,en;q=0.9",
    'User-Agent'     : "Mozilla/5.0 (Windows NT 10.0; Win64; x64;"
                       "PyWebcopyBot/{};)"
                       "AppleWebKit/604.1.38 (KHTML, like Gecko) "
                       "Chrome/68.0.3325.162".format(VERSION),
}

"""Default configuration with preconfigured values."""
default_config = {
    'debug'                : False,
    'log_file'             : None,
    'project_name'         : None,
    'project_folder'       : None,
    'over_write'           : False,
    'bypass_robots'        : False,
    'zip_project_folder'   : True,
    'delete_project_folder': False,
    'allowed_file_ext'     : safe_file_exts,
    'http_headers'         : safe_http_headers,
    'load_css'             : True,
    'load_javascript'      : True,
    'load_images'          : True,
    'download_size'        : 0,
    'robots_txt'           : None,
}


class ConfigHandler(CaseInsensitiveDict):
    """Provides functionality to the config instance which
    stores and provides configuration values in every module.
    """

    def __init__(self, *args, **kwargs):
        super(ConfigHandler, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<ConfigHandler: %s>' % self.get('project_name') or 'Default'

    def reset_config(self):
        """ Resets all to configuration to default state. """
        self._store = {}
        ConfigHandler.__init__(self)

    def setup_paths(self, project_folder, project_name):
        """ Easiest way to auto configure config keys for error free usage.
        Just provide the params and every other config key is automatically
        configured.

        Project name and project folder will be set as provided and
        rest of the configuration will also be updated if given.

        :param project_name: new name of the project
        :param project_folder: folder where to store all the downloaded files
        """

        if not self['project_name']:
            assert isinstance(project_name, str)
            self['project_name'] = project_name

        if not self['project_folder']:
            assert isinstance(project_folder, str)
            assert project_folder.find(os.path.sep) > -1, \
                "Project_folder path doesn't seem to be a valid path."
            self['project_folder'] = os.path.realpath(
                os.path.join(project_folder, self['project_name'])
            )

        if not os.path.exists(self['project_folder']):
            os.makedirs(self['project_folder'])

        # change the working directory so that no file is misplaced
        os.chdir(self['project_folder'])

        if not self['log_file']:
            self['log_file'] = os.path.join(self['project_folder'],
                                            self['project_name'] + '_log.log')

        level = (logging.DEBUG if self.get('debug', None) else logging.WARNING)
        LOGGER.addHandler(new_console_logger(level=level))
        LOGGER.addHandler(new_file_logger(self['log_file'], 'w'))

        # XXX: Do we need a html logger?
        # LOGGER.addHandler(new_html_logger(filename=os.path.join(
        # self['project_folder'], self['project_name'] + '_log.html')))

    def setup_config(self, project_url, project_folder, project_name, **kwargs):
        """Sets up the complete config parts which requires a project_url to be present.

        Complete configuration is done here and subject to change according to application structure
        You are advised to use only the .setup_path() method if you get any unusual behaviour

        :rtype: dict
        :returns: self
        """

        #: if external configuration is provided then
        #: the config dict will update its configuration
        #: values for global usages
        self.update(**kwargs)

        #: Updates the headers of the requests object, it is set to
        #: reflect this package as a copy bot
        #: by default which lets the server distinguish it from other
        #: requests and can help the maintainer to optimize the access
        SESSION.headers.update(self['http_headers'])

        #: Default base paths configuration is done right away so
        #: it at least sets base files and folder for downloading files
        self.setup_paths(project_folder, project_name or urlparse(project_url).hostname)

        #: Update the website access rules object which decide
        #: whether to access a site or not
        #: if you want to skip the checks then override the `bypass_robots` key
        # XXX user_agent = self['http_headers'].get('User-Agent', '*')
        user_agent = '*'    # for robots txt, a general useragent is better
        # prepared_robots_txt = RobotsTxtParser(user_agent, urljoin(project_url, '/robots.txt'))
        SESSION.set_robots_txt(user_agent, urljoin(project_url, '/robots.txt'))
        # self['robots_txt'] = prepared_robots_txt  # global ease access point

        #: Log this new configuration to the log file for debug purposes
        LOGGER.debug(str(dict(self)))
        return self

    def is_set(self):
        """Tells whether the configuration has been setup or not."""

        try:
            assert self.get('project_folder') is not None
            assert self.get('project_name') is not None
            assert self.get('log_file') is not None
        except AssertionError:
            return False
        else:
            return True


class DefaultConfig(ConfigHandler):
    """Config class with default configuration pre-populated.

    Use instance of this class if you want to customise the
    configuration.
    """

    __attrs__ = [
        'debug',
        'log_file',
        'project_name',
        'project_folder',
        'over_write',
        'bypass_robots',
        'zip_project_folder',
        'delete_project_folder',
        'allowed_file_ext',
        'http_headers',
        'load_css',
        'load_javascript',
        'load_images',
        'download_size',
    ]

    def __init__(self):
        super(DefaultConfig, self).__init__()

        #: Store default values of the keys for
        #: easing purposes
        for k, v in default_config.items():
            self.setdefault(k, v)

    def reset_config(self):
        super(DefaultConfig, self).reset_config()
        for k, v in default_config.items():
            self.setdefault(k, v)


config = DefaultConfig()
"""Global configuration instance."""


class AccessAwareSession(requests.Session):
    """
    Session object which consults robots.txt before
    accessing a resource.
    """
    def __init__(self):
        super(AccessAwareSession, self).__init__()
        self.stream = True
        self.robots_txt = None

    def set_robots_txt(self, user_agent, robot_txt_url):

        assert user_agent and robot_txt_url, "Please pass in valid arguments!"
        robots_parser = RobotsTxtParser(user_agent, robot_txt_url)
        #: We need the super method otherwise it will get stuck in a infinite loop
        setattr(robots_parser, '_get', super(AccessAwareSession, self).get)
        self.robots_txt = robots_parser
        self.robots_txt.read()

    def get(self, url, **kwargs):
        """
        Checks the access rules before sending the request.

        Returns
        -------
        Response or Dummy Response
        """

        if not self._can_access(url):
            raise AccessError("Access is not allowed by the site of url %s" % url)

        return super(AccessAwareSession, self).get(url, **kwargs)

    @lru_cache(maxsize=100)
    def _can_access(self, url):
        """ Determines if the site allows certain url to be accessed.
        """

        # If the robots class is not declared or is just empty instance
        # always return true

        if not self.robots_txt:
            return True
        if self.robots_txt.can_fetch(url):
            return True
        # Website may have restricted access to the certain url and if not in bypass
        # mode access would be denied
        else:

            if config.get('bypass_robots', False):
                # if explicitly declared to bypass robots then the restriction will be ignored
                LOGGER.warning("Forcefully Accessing restricted website part %s" % url)
                return True
            else:
                LOGGER.error("Website doesn't allow access to the url %s" % url)
                return False


SESSION = AccessAwareSession()
"""Global Session instance."""
