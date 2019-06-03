# -*- coding: utf-8 -*-

"""
pywebcopy.utils
~~~~~~~~~~~~~~~

Utils easing pywebcopy.
"""

import os
import re
import logging
from six.moves.urllib.parse import urljoin, urlsplit, urlparse
from six.moves.urllib.request import pathname2url, url2pathname

from configs import config

LOGGER = logging.getLogger('utils')
DEBUG = config['DEBUG']


validation_pattern = re.compile(r'[*":<>|?]+')


__all__ = [
    'filename_present', 'trace', 'netloc', 'url_path', 'url_port',
    'url_scheme', 'join_urls',
    'join_paths', 'relate', 'hostname', 'make_path',
    'compatible_path', 'get_filename', 'get_asset_filename',
    'file_path_is_valid', 'validation_pattern',
    'pathname2url', 'url2pathname',
]


def trace(func):
    """ Decorator prints function's name and parameters to screen in debug mode. """

    def wrapper(*args, **kwargs):

        if DEBUG:
            LOGGER.debug('TRACE: <func {}> called with {}, {}'.format(func.__name__, args, kwargs))

            func_result = func(*args, **kwargs)

            LOGGER.debug('TRACE: <func {}> returned {}'.format(func.__name__, func_result))

            return func_result
        else:
            return func(*args, **kwargs)
    return wrapper


@trace
def filename_present(url):
    """Checks whether a filename is present in the url/path or not."""

    if not url:
        return False
    if url.startswith(u'#'):
        return False

    url_obj = urlsplit(url)
    path = url_obj.path.strip('/')

    if url_obj.hostname == u'data' or not path:
        return False

    _possible_name = path.rsplit('/', 1)[-1]

    if not _possible_name or _possible_name.find('.') < 0:
        return False

    if len(_possible_name.rsplit('.', 1)[1]) < 1:
        return False

    return True


@trace
def netloc(url):
    """ Returns the domain of a url. """
    return urlparse(url).netloc


@trace
def url_path(url):
    """ Returns path of url after domain name """
    return urlparse(url).path


@trace
def url_scheme(url):
    """ Returns the protocol type e.g. http or https """
    return urlparse(url).scheme


@trace
def url_port(url):
    """ Returns the server port if defined in url. """
    return urlparse(url).port


@trace
def hostname(url):
    """ Returns domain name without server port. """
    return urlparse(url).hostname


@trace
def join_paths(a, *b):
    """ Returns joined path from two or more paths. """
    return os.path.join(a, *b)


@trace
def join_urls(a, *b):
    """ Returns joined url from two or more urls. """
    return urljoin(a, *b).replace('../', '')


@trace
def make_path(path):
    """ Makes a non-existing path and returns it. """

    if not os.path.exists(path):
        os.makedirs(path)

    return path


@trace
def compatible_path(url):
    """ Removes any protocol, port or any fragmentation from url. """
    return os.path.normcase(
        join_paths(
            hostname(url), url_path(url).lstrip('/')
        )
    )


@trace
def get_asset_filename(url):
    """ Returns file name of any asset file. """
    return get_filename(url_path(url))


@trace
def get_filename(url):
    """ Returns file name from url or path. """
    return os.path.split(url_path(url))[-1]


@trace
def get_file_ext(url):
    """ Returns extension of filename of the url or path """
    return get_filename(url).split('.')[-1]


@trace
def file_path_is_valid(file_path):
    """ Checks whether a file path is valid or not.

    Returns False if file_path contains
    any special chars e.g. ?<>{ etc.
    """

    _path_without_drive = os.path.splitdrive(file_path)[-1]

    if validation_pattern.match(_path_without_drive) is not None:
        return False

    return True


@trace
def relate(target_file, start_file):
    """ Returns relative path of target-file from start-file. """

    # Default os.path.relpath takes directories as argument, thus we need strip the filename
    # if present in the path else continue as is.
    target_dir = os.path.dirname(target_file)
    start_dir = os.path.dirname(start_file)

    # Calculate the relative path using the standard module and then concatenate the file names if
    # they were previously present.
    return os.path.join(os.path.relpath(target_dir, start_dir), os.path.basename(target_file))
