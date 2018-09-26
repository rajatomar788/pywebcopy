# -*- coding: utf-8 -*-

"""
pywebcopy.core
~~~~~~~~~~~~~~

* DO NOT TOUCH *

Core functionality of the pywebcopy engine.
"""


from datetime import datetime
import sys
import shutil
import zipfile
import os.path
try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse
from pywebcopy import VERSION
from pywebcopy import SESSION
from pywebcopy import LOGGER
from pywebcopy.exceptions import AccessError, ConnectionError
from pywebcopy.config import config


PY2 = True if sys.version_info.major == 2 else False
PY3 = True if sys.version_info.major == 3 else False


def zip_project():
    """Makes zip archive of project folder and returns the location.

    :returns: location of the zipped project_folder file.
    """

    # Project folder can be zipped based on preference
    # by default its set to True
    if config['zip_project_folder']:

        # make zip archive of all the files and not the empty folders
        archive = zipfile.ZipFile(
            os.path.abspath(config['project_folder']) + '.zip', 'w', zipfile.ZIP_DEFLATED)

        for dirn, _, fn in os.walk(config['project_folder']):
            # only files will be added to the zip archive instead of empty
            # folder which may be created during process
            for f in fn:

                try:
                    _temp_filename = os.path.join(dirn, f)
                    archive.write(
                        _temp_filename, _temp_filename[len(config['project_folder']):])

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
    if not config['_robots_obj'] or config['_robots_obj'].is_dummy:
        return True

    # Website may have restricted access to the certain url and if not in bypass
    # mode access would be denied
    elif not config['_robots_obj'].can_fetch(url):

        if not config['bypass_robots']:
            LOGGER.error("Website doesn't allow access to the url %s" % url)
            return False
        else:
            # if explicitly declared to bypass robots then the restriction will be ignored
            LOGGER.warning("Forcefully Accessing restricted website part %s" % url)
            return True
    else:
        return True


def get(url, *args, **kwargs):
    """ fetches contents from internet using `requests`.

    makes http request using custom configs
    it returns requests object if request was successful
    None otherwise.

    :param url: the url of the page or file to be fetched
    :returns: requests obj or None
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

    file_type = os.path.splitext(file_path or '')[-1]

    # Only specific for the html file types So that the comment does not pop up as
    # content on the page
    if file_type.lower() in ['.html', '.htm', '.xhtml', '.aspx', '.asp', '.php']:
        comment_style = '<!--#-->\n'
    elif file_type.lower() in ['.css', '.js', '.xml']:
        comment_style = '/*#*/\n'
    else:
        return b''

    mark = """
    * AerWebCopy Engine [version {}]
    * Copyright Aeroson Systems & Co.
    * File mirrored from {}
    * At UTC time: {}\n""".format(VERSION, file_path, datetime.utcnow())

    if PY3:
        return bytes(comment_style.replace('#', mark), 'utf8')
    else:
        return bytes(comment_style.replace('#', mark))


def new_file(location, content_url=None, content=None):
    """ Downloads any file to the disk.

    :rtype:
    :param location: path where to save the file

    :param content: contents or binary data of the file
    :OR:
    :param content_url: download the file from url

    :returns: location of downloaded file on disk if download was successful
    None otherwise
    """

    if not location or (content_url or content) is None:
        LOGGER.error("Location or Content for the file to be downloaded at %s is not of valid type!" % location)
        return
    '''
    if content and type(content) is not bytes:
        LOGGER.warning("Content for the file to be saved at %s is not of bytes type!" % location)

        # Try to convert content to bytes else will suppress the exception and return None
        try:
            if PY3:
                content = bytes(content, 'utf-8')
            else:
                content = bytes(content)
        except Exception as e:
            LOGGER.critical(e)
            LOGGER.critical("Can't convert the contents to bytes for the file %s" % location)
            return
    '''
    # Files can be of any types or can be large and hence to avoid downloading
    # those files you can configure which file types should be allowed to stored
    _file_ext = os.path.splitext(location or '')[-1].lower()

    if _file_ext not in config['allowed_file_ext']:
        LOGGER.critical('File of type %s is not allowed!' % _file_ext)
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
            content = req.content

        except Exception as e:
            LOGGER.error(e)
            LOGGER.error('Failed to load the content of file %s from %s' % (location, content_url))
            content = b'This File could not be downloaded because the server returned an error response!'

    _water_mark = _watermark(content_url or location)

    try:
        # Files can throw an IOError or similar when failed to open or write in that
        LOGGER.debug("Making path for the file at location %s" % location)
        if not os.path.exists(os.path.dirname(location)):
            os.makedirs(os.path.dirname(location))
        # case the function will catch it and log it then return None
        LOGGER.info("Writing file at location %s" % location)
        with open(location, 'wb') as f:
            f.write(content)

    except Exception as e:
        LOGGER.critical(e)
        LOGGER.critical("Download failed for the file of type %s to location %s" % (_file_ext, location))
        return

    LOGGER.info('File of type %s written successfully to %s' % (_file_ext, location))

    # The file location would be stored in the list for ease in querying the the download path
    # of a certain file
    config['downloaded_files'].append({content_url or content[:20]: location})

    return location
