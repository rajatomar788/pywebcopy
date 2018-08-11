# -*- coding: utf-8 -*-

"""
aerwebcopy.utils
~~~~~~~~~~~~~~~~

Utils easing aerwebcopy.
"""


import os
import re

import config
import core

if core.py2:
    from urlparse import urlparse, urljoin
elif core.py3:
    from urllib.parse import urlparse
    from urllib.parse import urljoin


__all__ = [
    'netloc', 'url_path', 'url_port', 'url_scheme', 'join_urls', 'join_paths',
    'relate', 'netloc_without_port', 'make_path', 'compatible_path', 'get_filename',
    'get_attr', 'get_asset_filename', 'file_path_is_valid'
]


@core.trace
def netloc(url):
    """ Returns the domain of a url. """
    return urlparse(url).netloc


@core.trace
def url_path(url):
    """ Returns path of url after domain name """
    return urlparse(url).path


@core.trace
def url_scheme(url):
    """ Returns the protocol type e.g. http or https """
    return urlparse(url).scheme


@core.trace
def url_port(url):
    """ Returns the server port if defined in url. """
    return urlparse(url).port


@core.trace
def netloc_without_port(url):
    """ Returns domain name without server port. """
    return netloc(url).split(':')[0]


@core.trace
def join_paths(a, *b):
    """ Returns joined path from two or more paths. """
    return os.path.join(a, *b)


@core.trace
def join_urls(a, *b):
    """ Returns joined url from two or more urls. """
    return urljoin(a, *b).replace('../', '')


@core.trace
def make_path(path):
    """ Makes a non-existing path and returns it. """

    if not os.path.exists(path):
        os.makedirs(path)
        core.now('Path Created Successfully! %s ' % path)

    elif os.path.exists(path):
        core.now('Path already exists!', level=2)

    else:
        core.now('Path creation failed!', level=4)

    return path


@core.trace
def compatible_path(url):
    """ Removes any protocol, port or any fragmentation from url. """
    return os.path.normcase(
        join_paths(
            netloc_without_port(url), url_path(url).strip('/')
        )
    )


@core.trace
def get_asset_filename(url):
    """ Returns file name of any asset file. """
    return get_filename(url_path(url))


@core.trace
def get_filename(url):
    """ Returns file name from url or path. """
    return os.path.split(url_path(url))[-1]


@core.trace
def get_file_ext(url):
    """ Returns extension of filename of the url or path """
    return get_filename(url).split('.')[-1]


@core.trace
def get_attr(soup_obj, attribute):
    """ Returns attribute of a html element. """
    return soup_obj.get(attribute, '')


@core.trace
def file_path_is_valid(file_path):
    """ Checks whether a file path is valid or not.

    Returns False if file_path contains
    any special chars e.g. $?#! etc.
    """

    _file_path_without_drive = os.path.splitdrive(file_path)[-1]

    if len(re.findall(config.config['filename_validation_pattern'], _file_path_without_drive)) != 0:

        core.now(
            'File path is not valid! "%s"' % _file_path_without_drive,
            level=3
        )
        return False

    core.now(
        'File path is valid! "%s"' % _file_path_without_drive,
        level=2
    )
    return True


@core.trace
def relate(target_file, start_file):
    """ Returns relative path of target-file from start-file. """

    core.now('Trying to relate paths :: \n%s\n%s' % (target_file, start_file))
    core.now('Start folder :: %s' % os.path.dirname(start_file))
    core.now('Target File :: %s' % target_file)

    try:
        rel_path = os.path.join(
            os.path.relpath(
                os.path.split(target_file)[0],
                os.path.split(start_file)[0]
            ), 
            os.path.basename(target_file)
        )

        core.now('resolved relative path :: %s' % rel_path)

    except ValueError:
        rel_path = './'

        core.now(
                'Error while relating path!', 
                level=4
            )

    return rel_path
