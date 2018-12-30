# -*- coding: utf-8 -*-

"""
pywebcopy.core
~~~~~~~~~~~~~~

* DO NOT TOUCH *

Core functionality of the pywebcopy engine.
"""

import os
import sys
import shutil
import zipfile
from textwrap import dedent
from datetime import datetime

import requests

from . import VERSION, SESSION, LOGGER
from .exceptions import AccessError, ConnectionError
from .configs import config


PY2 = True if sys.version_info.major == 2 else False
PY3 = True if sys.version_info.major == 3 else False


MARK = dedent("""
        {0}
        * AerWebCopy Engine [version {1}]
        * Copyright Aeroson Systems & Co.
        * File mirrored from {2}
        * At UTC time: {3}
        {4}
        """)


def zip_project():
    """Makes zip archive of current project folder and returns the location.

    :rtype: str
    :returns: location of the zipped project_folder file.
    """

    # make zip archive of all the files and not the empty folders
    archive = zipfile.ZipFile(
        os.path.abspath(config['project_folder']) + '.zip', 'w', zipfile.ZIP_DEFLATED)

    for dirn, _, fn in os.walk(config['project_folder']):
        # only files will be added to the zip archive instead of empty
        # folder which may be created during process
        for f in fn:

            try:
                new_fn = os.path.join(dirn, f)
                archive.write(
                    new_fn, new_fn[len(config['project_folder']):])

            except Exception as e:
                LOGGER.error(e)
                LOGGER.warning("Failed to add file to archive file %s" % f)

    archive.close()
    LOGGER.info('Saved the Project as ZIP archive at %s' % (config['project_folder'] + '.zip'))

    # Project folder can be automatically deleted after making zip file from it
    # this is True by default and will delete the complete project folder
    if config['delete_project_folder']:
        shutil.rmtree(config['project_folder'])


def _can_access(url):
    """ Determines if site allows certain url to be accessed.

    NOTE: It requires config['_robots_obj'] = structures.RobotsTxt object
    to be created first.
    """

    # If the robots class is not declared or is just empty instance
    # always return true
    if not config['_robots_obj']:
        return True

    elif config['_robots_obj'].can_fetch(url):
        return True

    # Website may have restricted access to the certain url and if not in bypass
    # mode access would be denied
    elif not config['_robots_obj'].can_fetch(url):

        if config['bypass_robots']:
            # if explicitly declared to bypass robots then the restriction will be ignored
            LOGGER.warning("Forcefully Accessing restricted website part %s" % url)
            return True
        else:
            LOGGER.error("Website doesn't allow access to the url %s" % url)
            return False
    else:
        return True


def get(url, *args, **kwargs):
    """ fetches contents from internet using `requests`.

    makes http request using custom configs
    it returns requests object if request was successful
    None otherwise.

    :param str url: the url of the page or file to be fetched
    :returns object: requests obj or None
    """

    # Make a check if url is meant for public viewing by checking for
    # the url in the /robots.txt file provided by site.
    if not _can_access(url):
        raise AccessError("Access is not allowed by the site of url %s" % url)

    try:
        # Usages the requests module to make a get request using a persistent session
        # object and returns that
        # otherwise on fail it returns None
        req = SESSION.get(url, *args, **kwargs)
        # log downloaded file size
        config['download_size'] += int(req.headers.get('content-length', 0))
        return req

    except Exception as e:
        LOGGER.error(e)
        LOGGER.error("Failed to access url at address %s" % url)
        return


def _watermark(file_path):
    """Returns a string wrapped in comment characters for specific file type."""

    file_type = os.path.splitext(file_path)[1] or ''

    # Only specific for the html file types So that the comment does not pop up as
    # content on the page
    if file_type.lower() in ['.html', '.htm', '.xhtml', '.aspx', '.asp', '.php']:
        comment_start = '<!--!'
        comment_end = '-->'
    elif file_type.lower() in ['.css', '.js', '.xml']:
        comment_start = '/*!'
        comment_end = '*/'
    else:
        return b''

    return MARK.format(comment_start, VERSION, file_path, datetime.utcnow(), comment_end).encode()


def new_file(location, content_url=None, content=None):
    """ Downloads any file to the disk.

    :param str location: path where to save the file

    :param bytes content: contents or binary data of the file
    :OR:
    :param str content_url: download the file from url

    :returns str: location of downloaded file on disk if download was successful
    None otherwise
    """

    req = None          # type: requests.Response

    if not location or (content_url or content) is None:
        LOGGER.error("Location or Content for the file to be downloaded at %s is not of valid type!" % location)
        return

    if content and type(content) is not bytes:
        LOGGER.warning("Content for the file to be saved at %s is not of bytes type!" % location)

        # Try to convert content to bytes else will suppress the exception and return None
        try:
            content = content.encode()      # type: bytes
        except Exception as e:
            LOGGER.critical(e)
            LOGGER.critical("Can't convert the contents to bytes for the file %s" % location)
            return

    # Files can be of any types or can be large and hence to avoid downloading
    # those files you can configure which file types should be allowed to stored
    _file_ext = os.path.splitext(location or '')[1].lower()

    if _file_ext not in config['allowed_file_ext']:
        LOGGER.critical('File ext %r is not allowed for file at %r' % (_file_ext, content_url or location))
        return

    # The file path provided can already be existing so only overwrite the files
    # when specifically configured to do so by config key 'over_write'
    if os.path.exists(location or ''):

        if not config['over_write']:
            LOGGER.error('File already exists at the location %s' % location)
            return location

        else:
            os.remove(location)
            LOGGER.info('ReDownloading the file of type %s to %s' % (_file_ext, location))
    else:
        LOGGER.info('Downloading a new file of type %s to %s' % (_file_ext, location))

    # Contents of the files can be supplied or filled by a content url
    # function we go online to download content from content url
    if not content and content_url is not None:
        LOGGER.info('Downloading content of file %s from %s' % (location, content_url))

        try:
            req = get(content_url, stream=True)
            # The file may not be available so will raise an error which will be caught by
            # except block an will return None
            if req is None or not req.ok:
                raise ConnectionError("File is not found or is unavailable on the server url %s" % content_url)

        except Exception as e:
            LOGGER.error(e)
            LOGGER.error('Failed to load the content of file %s from %s' % (location, content_url))
            content = b'This File could not be downloaded because the server returned an error response!'

    try:
        # Files can throw an IOError or similar when failed to open or write in that
        LOGGER.debug("Making path for the file at location %s" % location)
        if not os.path.exists(os.path.dirname(location)):
            os.makedirs(os.path.dirname(location))

    except OSError as e:
        LOGGER.critical(e)
        LOGGER.critical("Failed to create path for the file of type %s to location %s" % (_file_ext, location))
        return

    try:
        # case the function will catch it and log it then return None
        LOGGER.info("Writing file at location %s" % location)

        if hasattr(req, 'iter_content'):
            with open(location, 'wb') as f:
                # write in chunks to manage ram usages
                for chunk in req.iter_content(chunk_size=1024):
                    f.write(chunk)
                f.write(_watermark(content_url or location))
        else:
            with open(location, 'wb') as f:
                f.write(content)
                f.write(_watermark(content_url or location))

    except Exception as e:
        LOGGER.critical(e)
        LOGGER.critical("Download failed for the file of type %s to location %s" % (_file_ext, location))
        return

    LOGGER.success('File of type %s written successfully to %s' % (_file_ext, location))

    return location
