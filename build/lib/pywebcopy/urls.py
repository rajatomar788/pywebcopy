# -*- coding: utf-8 -*-

"""
pywebcopy.urls
~~~~~~~~~~~~~~

Deals with different types of urls in pywebcopy.parsers.

"""

import os.path
import re
import hashlib
from uuid import uuid4
from mimetypes import guess_extension
try:
    from urlparse import urlsplit, urljoin
    from urllib import url2pathname, pathname2url
except ImportError:
    from urllib.request import url2pathname, pathname2url
    from urllib.parse import urlsplit, urljoin
from pywebcopy.exceptions import InvalidUrlError
from pywebcopy.config import config
from pywebcopy import LOGGER


FILENAME_CLEANER = re.compile(r'[*":<>|?]+?\.\.?[/|\\]+')
URL_CLEANER = re.compile(r'[*"<>|]?\.\.?[/|\\]+')


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


def url2path(url, base_url=None, base_path=None, default_filename=None):
    """Converts urls to disk style file paths. """

    if not url:
        return

    if base_url:
        url = urljoin(base_url or '', url)

    if not filename_present(url):
        url = urljoin(url, default_filename or str(uuid4())[:10] + '.download')
    
    url_obj = urlsplit(url)

    if url_obj.hostname == 'data':
        return

    url = "%s%s" % (url_obj.hostname or '', url_obj.path or '')
    
    if not url:
        return

    path = FILENAME_CLEANER.sub('_', url)
    
    if base_path:
        path = os.path.join(base_path or '', path)

    return path


class Url(object):
    """Provides several operations on a url. """

    def __init__(self, url):

        if not url:
            raise InvalidUrlError("Url is invalid %s" % url)

        self._unique_fn_required = config['unique_filenames']
        self.original_url = url
        self.default_filename = self.hash() + (guess_extension(url) or '.download')
        self.url = url
        self._base_url = ''
        self._base_path = ''

    def __str__(self):
        return self.url

    def __repr__(self):
        return "<Url({})>".format(self.original_url)

    def hash(self):
        return str(int(hashlib.sha1(self.original_url).hexdigest(), 16) % (10 ** 8))

    @property
    def parsed_url(self):
        """Parses the url in six part tuple."""
        return urlsplit(self.url, allow_fragments=False)

    @property
    def hostname(self):
        return self.parsed_url.hostname

    @property
    def port(self):
        return self.parsed_url.port

    @property
    def url_path(self):
        return self.parsed_url.path.split('#', 1)[0]

    @property
    def scheme(self):
        return self.parsed_url.scheme

    def _join_with(self, other_url):
        """Joins this url with new url. """
        return urljoin(other_url or '', self.url)

    @property
    def base_url(self):
        """Returns the base url this url if set."""
        if self._base_url:
            return self._base_url
        return ''

    @base_url.setter
    def base_url(self, base_url):
        """Converts self.url to join result of self.url and provided base_url"""
        self._base_url = base_url or ''
        self.url = URL_CLEANER.sub('', self._join_with(self.base_url or ''))
        LOGGER.debug('Base url of Url obj %s is now set to %s now self.url is %s' % (self, self.base_url, self.url))

    @property
    def base_path(self):
        """Returns the base path if set."""
        if self._base_path:
            return self._base_path
        return ''

    @base_path.setter
    def base_path(self, base_path):
        """Sets a base for the return value of file_path() function."""
        self._base_path = base_path or ''

    @property
    def to_path(self):
        """Returns a file path made from url."""
        if self.base_path:
            return os.path.join(self.base_path, url2pathname(self.hostname + self.url_path))
        return url2pathname(self.hostname + self.url_path)

    @property
    def file_name(self):
        """Returns a file name from url url_path."""
        # Web pages can be displayed without any file name So a default
        # file name is required in case.

        if not filename_present(self.url):
            return self.default_filename
        else:
            return os.path.split(self.to_path)[-1]

    @property
    def file_path(self):
        """Returns a path with filename if not already present in the url to store the Content. """

        # Either of the filename or default_filename needs to be present

        if not self.file_name:
            raise InvalidUrlError("File name is not present in url %s" % self.url)

        # default path generated for the url by the function
        _path = FILENAME_CLEANER.sub('', self.to_path)

        # If the default file name is used then it is not definitely
        # present in the url and hence to be joined to the _path
        if not _path.endswith(self.file_name):
            if self._unique_fn_required:
                path = os.path.join(_path, self.hash() + "__" + self.file_name)
            else:
                path = os.path.join(_path, self.file_name)
        else:
            if self._unique_fn_required:
                path = _path.replace(self.file_name, os.path.join(self.hash() + "___" + self.file_name))
            else:
                path = _path

        LOGGER.debug("Url obj for %s generated file path %s" % (self, path))

        return path
