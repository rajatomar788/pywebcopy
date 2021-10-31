# Copyright 2020; Raja Tomar
# See license for more details
import logging
import os
import sys
import tempfile
from functools import partial

from requests.structures import CaseInsensitiveDict
from six import text_type
from six import string_types

from .__version__ import __title__
from .__version__ import __version__
from .urls import HIERARCHY
from .urls import get_host
from .urls import secure_filename
from .session import default_headers

__all__ = [
    'ConfigHandler',
    'get_config',
    'default_config',
    'safe_file_types',
    'safe_http_headers'
]

logger = logging.getLogger(__name__)


def add_stderr_logger(name=__title__, level=logging.DEBUG):
    """
    Helper for quickly adding a StreamHandler to the logger. Useful for
    debugging.

    Returns the handler after adding it.
    """
    # This method needs to be in this __init__.py to get the __name__ correct
    # even if this library is wrapped within another package.
    root = logging.getLogger(name)
    #: If there is already a stderr logger then we don't need to bother.
    for h in root.handlers:
        if isinstance(h, logging.StreamHandler):
            if h.stream == sys.stderr:
                h.disabled = False
                h.setLevel(level)
                return h
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            '%(levelname)-8s - %(name)s:%(lineno)d - %(message)s'
        )
    )
    root.addHandler(handler)
    root.setLevel(level)
    root.debug('Added a stderr logging handler to logger: %s', name)
    return handler


# FIXME: Do something about these.
safe_file_types = [
    'text/*',
    'image/*',
    'font/*',
    'application/pdf',
    'application/json',
]


safe_http_headers = {
    "Accept-Language": "en-US,en;q=0.9",
    'User-Agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) "
        "Gecko/20100101 Firefox/70.0 PyWebCopyBot/%s" % __version__
}

#: Base configuration with preconfigured values.
default_config = {
    'debug': False,
    'project_url': None,
    'project_name': None,
    'project_folder': None,
    'threaded': None,
    'thread_join_timeout': None,
    'tree_type': HIERARCHY,

    # TODO: Allow a `last-modified-time` overwrite mode
    'overwrite': False,

    'bypass_robots': False,
    'http_cache': False,
    'http_headers': default_headers(**safe_http_headers),
    'delay': None,

    # TODO: Disabled for now until I figure it out.
    # 'allowed_file_types': safe_file_types,

    # TODO: domain blocking and whitelisting
}


class ConfigError(AttributeError, TypeError):
    """Bad config value or operation."""


class ConfigHandler(CaseInsensitiveDict):
    """Provides functionality to the config instance which
    stores and provides configuration values in every module.
    """
    def __repr__(self):  # pragma: no cover
        return '<ConfigHandler(%s)>' % self.get('project_name', 'Not Set')

    def __getattribute__(self, item):
        """Dynamic method of name `get_(key)` and `set_(key)` generation
        for all of the keys available.
        for example to change the `project_url` key
        instead of using dictionary like operation you would do
        `.get_project_url()` instead of `['project_url']`.
        `.set_project_url(new)` instead of `['project_url'] = new`.
        """
        if isinstance(item, string_types) and item.startswith('set_'):
            if item[4:] in self:
                return partial(self.__setitem__, item[4:])
        elif isinstance(item, string_types) and item.startswith('get_'):
            if item[4:] in self:
                return partial(self.__getitem__, item[4:])
        return super(ConfigHandler, self).__getattribute__(item)

    def resolve_url(self):
        """Resolves any redirects in the url and sets the final url as base url."""
        raise NotImplementedError()

    def reset_config(self):
        """Resets all to configuration to default state."""
        self.update(default_config)

    def reset_key(self, key):
        self.update({key: default_config.get(key)})

    def is_set(self):
        """Checks whether the configuration has required attributes or not."""
        try:
            assert self.get('project_folder') is not None
            assert self.get('project_url') is not None
            assert self.get('project_name') is not None
        except AssertionError:
            return False
        else:
            return True

    def setup_paths(self, project_folder, project_name):
        """Fills the project_name, project_name and its
        dependent keys after evaluation.

        .. version changed :: 6.0.0
            Added string type checks and os based path normalising.

        .. version changed :: 6.1.0
            FIX: fixed path issue when using relative path for project_folder

        .. version changed :: 6.3.0
            FIX: Removed file based logging.
            FIX: Disabled dir change on setup

        :param project_name: new name of the project
        :param project_folder: folder where to store all the downloaded files
        """
        if not isinstance(project_name, string_types):
            raise ConfigError("project_name value must be a string")

        if not isinstance(project_folder, string_types):
            raise ConfigError("project_folder value must be a string!")

        if os.altsep:
            project_folder = project_folder.replace(os.altsep, os.sep)
        if project_folder.find(os.sep) < 0:  # pragma: no cover
            raise ConfigError("Project_folder path doesn't seem to be a valid path.")

        project_folder = os.path.abspath(project_folder)

        norm_p = os.path.join(
            os.path.normpath(project_folder),
            os.path.normpath(project_name)
        )
        self.set_project_name(project_name)
        self.set_project_folder(norm_p)

        if not os.path.exists(norm_p):
            os.makedirs(norm_p)

    def setup_config(self,
                     project_url=None,
                     project_folder=None,
                     project_name=None,
                     overwrite=False,
                     bypass_robots=False,
                     debug=False,
                     delay=None,
                     threaded=None):
        """Sets up the complete config parts which requires a project_url to be present.

        Complete configuration is done here and subject to change according to application structure
        You are advised to use only the .setup_path() method if you get any unusual behaviour
        """
        self.set_overwrite(overwrite)
        self.set_bypass_robots(bypass_robots)
        self.set_debug(debug)
        self.set_delay(delay)
        self.set_threaded(threaded)
        self.set_project_url(project_url)
        self.setup_paths(project_folder, project_name)

        #: Add a stderr logger to this library.
        if debug:
            add_stderr_logger(level=logging.DEBUG)

        #: Log this new configuration to the log file for debug purposes
        logger.debug(str(dict(self)))

    def create_context(self):
        if not self.is_set():
            raise ConfigError("Config is missing required attributes!")
        from .urls import Context
        return Context.from_config(self)

    def create_session(self):
        if not self.is_set():
            raise ConfigError("Config is missing required attributes!")
        from .session import Session
        return Session.from_config(self)

    def create_crawler(self):
        if not self.is_set():
            raise ConfigError("Config is missing required attributes!")
        from .core import Crawler
        return Crawler.from_config(self)

    def create_page(self):
        if not self.is_set():
            raise ConfigError("Config is missing required attributes!")
        from .core import WebPage
        return WebPage.from_config(self)


def get_config(project_url,
               project_folder=None,
               project_name=None,
               bypass_robots=False,
               debug=False,
               delay=None,
               threaded=None):
    """Create a ConfigHandler instance and return it.
    If the project_folder is not supplied it will use the users Tempdir.

    :param project_url: project_url of the web page to work with
    :type project_url: str
    :param project_folder: folder in which the files will be downloaded
    :type project_folder: str
    :param project_name: name of the project to distinguish it
    :type project_name: str | None
    :param bypass_robots: whether to follow the robots.txt rules or not
    :param debug: whether to print deep logs or not.
    :param delay: amount of delay between two concurrent requests to a same server.
    :param threaded: whether to use threading or not (it can break some site).
    """
    if not isinstance(project_url, string_types):
        raise ConfigError("Expected string type, got %r" % project_url)
    if project_folder and not isinstance(project_folder, string_types):
        raise ConfigError("Expected string type, got %r" % project_folder)

    if not project_folder:
        logger.debug('No project folder provided, %temp% dir will be used instead.')
        project_folder = tempfile.gettempdir()

    if not project_name:
        project_name = '_'.join(
            map(secure_filename,
                map(lambda x: text_type(x),
                    filter(None, get_host(project_url)))))
        logger.debug('No project name provided, generated from url: %s' % project_name)

    ans = ConfigHandler(default_config)
    ans.setup_config(
        project_url=project_url,
        project_folder=project_folder,
        project_name=project_name,
        bypass_robots=bypass_robots,
        debug=debug,
        delay=delay,
        threaded=threaded,
    )
    return ans
