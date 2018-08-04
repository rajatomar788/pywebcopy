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
    'get_attribute', 'get_stylefile_name', 'file_path_is_valid'
]


# toolkit func to get netloc of url
def netloc(url):
    return urlparse(url).netloc


# toolkit func to get path of url after domain name
def url_path(url):
    return urlparse(url).path


# toolkit func to get connection type of url
# e.g. https or http
def url_scheme(url):
    return urlparse(url).scheme


# toolkit func to get connection port of server
def url_port(url):
    return urlparse(url).port


def netloc_without_port(url):
    return netloc(url).split(':')[0]


# toolkit func to join two or more paths
def join_paths(a, *b):
    return os.path.join(a, *b)


# toolkit func to join two or more paths
def join_urls(a, *b):

    core.now('Joining urls %s %s' % (a, b))
    joined_url = urljoin(a, *b).replace('../', '')
    core.now('Joined to %s' % joined_url)

    return joined_url


# toolkit func to make sure files end up in correct dir
def make_path(path):

    core.now('Checking Path :: %s' % path)

    if not file_path_is_valid(path):
        return

    if not os.path.exists(path):
        try:
            os.makedirs(path)
            core.now('Path Created Successfully!')

        except WindowsError:
            core.now(
                'Path creation failed! Requested path was too long or Invalid! Path %s'
                % path,
                level=4
            )        

    elif os.path.exists(path):
        core.now('Path already exists!', level=2)

    else:
        core.now('Path creation failed!', level=4)

    return path


# toolkit func to create paths which does not raise errors
def compatible_path(url):

    # remove any error prone [?query or #fragment or :port] part from url
    return os.path.normpath(
        os.path.join(
            netloc_without_port(url), url_path(url).strip('/')
        )
    )


# toolkit func to return file names of stylesheets and js
def get_stylefile_name(url):

    path = url_path(url)
    # return the last elem
    filename = os.path.split(path)[1]

    return filename


# toolkit func to return filename of the url or path
def get_filename(url):
    return os.path.split(url_path(url))[1]


# checks whether a file path is valid or not
def file_path_is_valid(file_path):

    """Returns False if file_path contains
    any special chars e.g. $?#! etc.
    """

    _file_path_without_drive = os.path.splitdrive(file_path)[1]

    if len(re.findall(config.config['filename_validation_pattern'], _file_path_without_drive)) != 0:

        core.now(
            'File path %s is not valid!' % _file_path_without_drive, 
            level=3
        )
        return False

    core.now(
        'File path %s is valid!' % _file_path_without_drive, 
        level=2
    )
    return True


# toolkit func to return attribute of a html element
def get_attribute(soup_obj, attribute):
    # return value or empty string
    return soup_obj.get(attribute, '')


# toolkit func to relate two file paths
def relate(target_file, start_file):

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

        if rel_path.endswith('/'):
            rel_path += 'index.html'

        core.now('resolved relative path :: %s' % rel_path)

    except ValueError:
        rel_path = './'
        core.now(
            'Error while relating path!', 
            level=4
        )

    return rel_path
