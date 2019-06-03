# -*- coding: utf-8 -*-

"""
pywebcopy.config
~~~~~~~~~~~~~~~~

Modifies the behaviour of pywebcopy.

"""
import logging
import os
from io import BytesIO

import requests

from .compat import urlparse, urljoin
from .exceptions import AccessError
from .globals import safe_file_exts, safe_http_headers
from .structures import CaseInsensitiveDict, RobotsTxtParser

__all__ = ['default_config', 'config', 'SESSION', 'AccessAwareSession']

LOGGER = logging.getLogger('config')

"""Default configuration with preconfigured values."""
default_config = {
    'debug': False,
    'log_file': None,
    'project_name': None,
    'project_folder': None,
    'over_write': False,
    'bypass_robots': False,
    'zip_project_folder': True,
    'delete_project_folder': False,
    'allowed_file_ext': safe_file_exts,
    'http_headers': safe_http_headers,
    'load_css': True,
    'load_javascript': True,
    'load_images': True,
    'download_size': 0,
    'join_timeout': None,
    'robots_txt': None,
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
        CaseInsensitiveDict.__init__(self)

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

    def reset_key(self, key):
        """Resets a specific key to its default state.

        .. new in version :: 6.0.0

        """
        self[key] = default_config.get(key)

    def setup_paths(self, project_folder, project_name):
        """Fills the project_name, project_name and its
        dependent keys after evaluation.

        .. version changed :: 6.0.0
            Added string type checks and os based path normalising.

        :param project_name: new name of the project
        :param project_folder: folder where to store all the downloaded files
        """

        if not isinstance(project_name, str):
            raise TypeError("project_name value must be a string")

        if not isinstance(project_folder, str):
            raise TypeError("project_folder value must be a string!")

        if os.altsep:
            project_folder = project_folder.replace(os.altsep, os.sep)

        if not project_folder.find(os.sep) > -1:
            TypeError("Project_folder path doesn't seem to be a valid path.")

        norm_p = os.path.join(
            os.path.normpath(project_folder),
            os.path.normpath(project_name)
        )

        self.__setitem__('project_name', project_name)
        self.__setitem__('project_folder', norm_p)
        # print(norm_p)

        if not os.path.exists(norm_p):
            os.makedirs(norm_p)

        # change the working directory so that no file is misplaced
        os.chdir(norm_p)

        lf = os.path.join(norm_p, 'pywebcopy_log.log')

        if os.path.exists(lf):
            try:
                os.unlink(lf)
            except OSError:
                # Just gonna leave it for default logger to figure out
                pass

        self.__setitem__('log_file', lf)

        # Console loggers (StreamHandlers) levels would be tuned
        if self.get('debug') is True:
            for handler in logging.root.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(logging.DEBUG)

        # Add a new file logger to the root logger
        f_stream = logging.FileHandler(lf, 'w')
        f_stream.setLevel(logging.DEBUG)
        f_stream.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s.%(funcName)s:%(lineno)d - %(message)s",
                "%d-%b-%Y %H:%M:%S"
            )
        )
        logging.root.addHandler(f_stream)

    def setup_config(self, project_url=None, project_folder=None, project_name=None,
                     over_write=False, bypass_robots=False, zip_project_folder=True,
                     delete_project_folder=False, load_css=True, load_javascript=True,
                     load_images=True, join_timeout=None, log_file=None, debug=False):
        """Sets up the complete config parts which requires a project_url to be present.

        Complete configuration is done here and subject to change according to application structure
        You are advised to use only the .setup_path() method if you get any unusual behaviour

        :rtype: dict
        :returns: self
        """

        #: if external configuration is provided then
        #: the config dict will update its configuration
        #: values for global usages
        self.update(
            project_url=project_url,
            over_write=over_write, bypass_robots=bypass_robots, zip_project_folder=zip_project_folder,
            delete_project_folder=delete_project_folder, load_css=load_css, load_javascript=load_javascript,
            load_images=load_images, join_timeout=join_timeout, debug=debug, log_file=log_file
        )

        #: Default base paths configuration is done right away so
        #: it at least sets base files and folder for downloading files
        if not project_name:
            project_name = urlparse(project_url).hostname

        self.setup_paths(project_folder, project_name)

        #: Log this new configuration to the log file for debug purposes
        LOGGER.debug(str(dict(self)))

        #: Updates the headers of the requests object, it is set to
        #: reflect this package as a copy bot
        #: by default which lets the server distinguish it from other
        #: requests and can help the maintainer to optimize the access
        SESSION.headers.update(self.get('http_headers'))
        SESSION.set_bypass(self.get('bypass_robots'))
        #: Update the website access rules object which decide
        #: whether to access a site or not
        #: if you want to skip the checks then override the `bypass_robots` key
        # XXX user_agent = self['http_headers'].get('User-Agent', '*')
        # prepared_robots_txt = RobotsTxtParser(user_agent, urljoin(project_url, '/robots.txt'))
        getattr(SESSION, '_setup_parser')(urljoin(project_url, '/robots.txt'))

        return self


config = ConfigHandler(**default_config)
"""Global configuration instance."""


class AccessAwareSession(RobotsTxtParser, requests.Session):
    """
    Session object which consults robots.txt before
    accessing a resource.
    """

    def __init__(self):
        RobotsTxtParser.__init__(self)
        requests.Session.__init__(self)
        self.stream = True

        self._bypass = False
        self._parser = None
        self._parser_ready = False
        self._parser_broken = False
        self._bytes = 0  # total data transfer
        self.hooks['response'] = self.log_response

    def get(self, url, **kwargs):
        self._access_check(url)
        return self._get(url, **kwargs)

    def get_or_dummy(self, url, **kwargs):
        self._access_check(url)
        try:
            resp = super(AccessAwareSession, self).get(url, **kwargs)
        except requests.exceptions.RequestException as err:
            LOGGER.error("Failed to access url at address [%s] exception \n %s" % (url, err))
            resp = self._dummy_resp(err)
        return resp

    def _setup_parser(self, robots_txt_url):
        assert isinstance(robots_txt_url, str), "Please pass in valid arguments!"

        self.set_url(robots_txt_url)
        self.read()
        self._parser_ready = True

    def set_bypass(self, bypass):
        self._bypass = bool(bypass)

    def log_response(self, resp, **_kwargs):
        LOGGER.info('Got response %r from %s', resp, resp.url)
        self._bytes += int(resp.headers.get('Content-length', 0))

    @staticmethod
    def _dummy_resp(err):
        """
        Return dummy data so that a dummy file will always be downloaded
        """
        resp = requests.Response()
        resp.raw = BytesIO(
            ('[This File could not be downloaded.]\n'
             '[Reason: ] \n\n %r \n\n' % str(err)).encode()
        )
        resp.encoding = 'utf-8'  # plain encoding
        resp.status_code = 200  # fake the status
        resp.is_dummy = True  # but leave a mark
        resp.reason = str(err)  # fail reason
        return resp

    def _get(self, url, **kwargs):
        """
        Raw get method.
        """
        return self.request('GET', url, **kwargs)

    def _access_check(self, url):
        if not self._can_access(url):
            raise AccessError("Access is not allowed by the site of url %s" % url)

    def _can_access(self, url):
        """ Determines if the site allows certain url to be accessed.
        """

        # If the robots class is not declared or is just empty instance
        # always return true
        if self._parser_broken:
            return True
        if not self._parser_ready:
            # warnings.warn("Robots Parser not set up!")
            # self._parser_broken = True
            return True
        if self.can_fetch(url):
            return True
        # Website may have restricted access to the certain url and if not in bypass
        # mode access would be denied
        else:
            if self._bypass:
                # if explicitly declared to bypass robots then the restriction will be ignored
                LOGGER.warning("Forcefully Accessing restricted website part %s" % url)
                return True
            else:
                LOGGER.error("Website doesn't allow access to the url %s" % url)
                return False


SESSION = AccessAwareSession()
"""Global Session instance."""
