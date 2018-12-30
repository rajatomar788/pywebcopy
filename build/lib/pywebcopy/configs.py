# -*- coding: utf-8 -*-

"""
pywebcopy.config
~~~~~~~~~~~~~~~~

Modifies the behaviour of pywebcopy.

"""


__all__ = ['default_config', 'config', 'ConfigHandler']


import os

from six.moves.urllib.parse import urlparse, urljoin

from . import VERSION, SESSION, LOGGER
from .logger import new_file_logger, new_html_logger
from .structures import CaseInsensitiveDict, RobotsTxt


"""Store the default config for initialising and backup."""
default_config = {
    'debug': True,
    'log_file': None,
    'project_name': None,
    'project_folder': None,
    'over_write': False,
    'bypass_robots': True,
    'zip_project_folder': True,
    'delete_project_folder': False,
    'allowed_file_ext': ['.html', '.php', '.asp', '.aspx', '.htm', '.xhtml', '.css',
                         '.json', '.js', '.xml', '.svg', '.gif', '.ico', '.jpeg', '.pdf',
                         '.jpg', '.png', '.ttf', '.eot', '.otf', '.woff', '.woff2', '.download', '.pwcf'],
    'parser': 'lxml',
    'http_headers': {
        "Accept-Language": "en-US,en;q=0.9",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; PyWebcopyBot/{};) "
                      "AppleWebKit/604.1.38 (KHTML, like Gecko) Chrome/68.0.3325.162".format(VERSION),
        },
    'load_css': True,
    'load_javascript': True,
    'load_images': True,
    'download_size': 0,
    'downloaded_files': list(),
    '_robots_obj': None,
}


class ConfigHandler(CaseInsensitiveDict):
    """Provides functionality to the config instance which
    stores and provides configuration values in every module.

    """

    def __init__(self, *args, **kwargs):
        super(ConfigHandler, self).__init__(*args, **kwargs)

    def reset_config(self):
        """ Resets all to configuration to default state. """
        self._store = ConfigHandler(default_config)

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
            self['project_name'] = project_name

        if not self['project_folder']:
            self['project_folder'] = os.path.realpath(os.path.join(project_folder, self['project_name']))

        if not os.path.exists(self['project_folder']):
            os.makedirs(self['project_folder'])

        os.chdir(self['project_folder'])

        if not self['log_file']:
            self['log_file'] = os.path.join(self['project_folder'], self['project_name'] + '_log.log')

        LOGGER.addHandler(new_file_logger(self['log_file'], 'w'))
        LOGGER.addHandler(new_html_logger(filename=os.path.join(self['project_folder'],
                                                                self['project_name'] + '_log.html')))

    def setup_config(self, project_url, project_folder, project_name, **kwargs):
        """Sets up the complete config parts which requires a project_url to be present.

        Complete configuration is done here and subject to change according to application structure
        You are advised to use only the .setup_path() method if you get any unusual behaviour

        :rtype: dict
        :returns: a fresh dictionary object for use in custom configurations
        """

        # if external configuration is provided then the config dict will update its configuration
        # values for global usages
        self.update(**kwargs)

        # Updates the headers of the requests object, it is set to reflect this package as a copy bot
        # by default which lets the server distinguish it from other requests and can help the maintainer
        # to optimize the access
        SESSION.headers.update(self['http_headers'])

        # Default base configuration is done right away so it at least sets base files and folder
        self.setup_paths(project_folder, project_name or urlparse(project_url).hostname)

        # Update the website access rules object which decide whether to access a site or not
        # if you want to skip the checks then override this key to None after the setup_config has complete
        self['_robots_obj'] = RobotsTxt('*', urljoin(project_url, '/robots.txt'))

        # Log this new configuration to the log file for debug purposes
        LOGGER.debug(dict(self))

        # Return a copy of configuration for any use
        return dict(self)


config = ConfigHandler(default_config)
"""Global configuration instance."""
