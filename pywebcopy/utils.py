# -*- coding: utf-8 -*-

"""
aerwebcopy.utils
~~~~~~~~~~~~~~~~

Utils easing aerwebcopy.
"""

import os
import re
import functools


from pywebcopy import config
debug = config.config['debug']
validation_pattern = config.config['filename_validation_pattern']
del config


try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse
    from urllib.parse import urljoin


__all__ = [
    'trace', 'netloc', 'url_path', 'url_port', 'url_scheme', 'join_urls', 
    'join_paths', 'relate', 'hostname', 'make_path',
    'compatible_path', 'get_filename', 'get_attr', 'get_asset_filename', 
    'file_path_is_valid'
]


def trace(func):
    """ Decorator prints function's name and parameters to screen in debug mode. """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        if debug:
            print('TRACE: <func {}> called with {}, {}'.format(func.__name__, args, kwargs))

            func_result = func(*args, **kwargs)

            print('TRACE: <func {}> returned {}'.format(func.__name__, func_result))

            return func_result
        else:
            return func(*args, **kwargs)
    return wrapper


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
            hostname(url), url_path(url).strip('/')
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
def get_attr(soup_obj, attribute):
    """ Returns attribute of a html element. """
    return soup_obj.get(attribute, '')


@trace
def file_path_is_valid(file_path):
    """ Checks whether a file path is valid or not.

    Returns False if file_path contains
    any special chars e.g. ?<>{ etc.
    """

    _path_without_drive = os.path.splitdrive(file_path)[-1]

    from pywebcopy.core import now

    if validation_pattern.match(_path_without_drive) is not None:
        now(
            'File path is not valid! "%s"' % _path_without_drive,
            level=3
        )
        return False

    now(
        'File path is valid! "%s"' % _path_without_drive,
        level=2
    )

    del now

    return True


@trace
def relate(target_file, start_file):
    """ Returns relative path of target-file from start-file. """

    try:
        rel_path = os.path.join(
            os.path.relpath(
                os.path.split(target_file)[0],
                os.path.split(start_file)[0]),
            os.path.basename(target_file)
        )

    except ValueError:
        rel_path = ''

    return rel_path
