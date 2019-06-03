# -*- coding: utf-8 -*-

"""
pywebcopy.urls
~~~~~~~~~~~~~~

Parses urls.

"""

import logging
import hashlib
import itertools
import os
import re

from .compat import (
    urljoin,
    unquote,
    urldefrag,
    urlsplit,
    url2pathname,
    basestring)

__all__ = ['URLTransformer', 'filename_present', 'url2path', 'relate']


# Removes the non-fileSystem compatible letters or patterns from a file path
FILENAME_CLEANER = re.compile(r'[*":<>|?]+?\.\.?[/|\\]+')

# Cleans query params or fragments from url to make it look like a path
URL_CLEANER = re.compile(r'[*"<>|]?\.\.?[/|\\]+(?:[#]\S+)')

# Matches any special character like #, : etc.
SPECIAL_CHARS = re.compile(r'(?:[*\"<>|!$&:?])+?')  # any unwanted char

# Matches any fragment or query data in url
URL_FRAG = re.compile(r'(?:[#?;=]\S+)?')  # query strings

# Matches any relative path declaration i.e. '../', './' etc.
RELATIVE_PATHS = re.compile(r'(?:\.+/+)+?')  # relative paths


LOGGER = logging.getLogger('urls')


def filename_present(url):
    """Checks whether a `filename` is present in the url/path or not.

    :param str url: url string to check the file name in.
    :return boolean: True if present, else False
    """

    if not url:
        return False
    if url.startswith(u'#'):
        return False

    url_obj = urlsplit(url)
    url = url_obj.path
    if url_obj.hostname == u'data' or not url:
        return False

    i = len(url)
    while i and url[i - 1] not in '/\\':
        i -= 1
    fn = url[i:]

    if fn.strip() == '':
        return False
    if i == 0:
        return False

    return True


def url2path(url, base_url=None, base_path=None, default_filename=None):
    """Converts urls to disk style file paths. """

    if not url:
        return

    if base_url:
        url = urljoin(base_url or '', url)

    if not filename_present(url):
        url = urljoin(url, default_filename)

    url_obj = urlsplit(url)

    if url_obj.hostname == 'data':
        return

    url = "%s%s" % (url_obj.hostname, url_obj.path)

    if not url:
        return

    path = FILENAME_CLEANER.sub('_', url)

    if base_path:
        path = os.path.join(base_path or '', path)

    return path


# Counter for generating distinguishable file names.
counter = itertools.count().__next__


def make_path_from_url(url, base_url=None, base_path=None, default_fn=None):
    return URLTransformer(url, base_url, base_path, default_fn).file_path


class URLTransformer(object):
    """Transforms url into various types and subsections.

    :param str url: a url to perform transform operations on
    :param str base_url: parent url of the given url, if any.
    :param str base_path: absolute path to be added to new paths generated.
    :param str default_fn: filename to use when there is no filename present in url
    """

    __attrs__ = [
        'url', 'default_suffix', 'file_path',
        'enforce_suffix', 'default_stem',
        'parsed_url', 'hostname', 'port', 'url_path', 'scheme',
        'base_url', 'base_path', 'to_path',
    ]

    __slots__ = 'default_stem', 'default_suffix', 'enforce_suffix', '_id', \
                '_base_url', '_base_path', '_default_fn', '_url',

    def __init__(self, url, base_url=None, base_path=None, default_fn=None):

        # manual type checking for url
        if not isinstance(url, basestring):
            raise TypeError("Url must be of string type!")
        try:
            url = unquote(url)
        except AttributeError:
            raise

        # default place holders
        self._url = url
        self._base_url = None
        self._base_path = None
        self._id = self._hex()
        self.default_stem = "file_" + self._id
        self.default_suffix = 'pwc'
        self.enforce_suffix = False
        self._default_fn = default_fn

        # properties with type checks
        if base_url is not None:
            self.base_url = base_url
        if base_path is not None:
            self.base_path = base_path

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.__init__(*args, **kwargs)
        # using it here instead of __init__ will get the subclasses
        # attribute overrides correct
        LOGGER.debug('Making new <UrlTransformer> with values: ' + str(obj))
        return obj

    def __str__(self):
        return {a: getattr(self, a) for a in self.__attrs__}.__str__()

    def __repr__(self):
        return "<URLTransformer(%r, %r, %r, %r)>" % (
            self._url, self.base_url, self.base_path, self._default_fn
        )

    def __reduce__(self):
        return self.__class__.__name__, {a: getattr(self, a) for a in self.__slots__}

    @property
    def default_filename(self):
        """Makes a unique default name based on suffix."""
        if not self._default_fn:
            return "%s.%s" % (self.default_stem, self.default_suffix)
        return self._default_fn

    @default_filename.setter
    def default_filename(self, o):
        assert isinstance(o, str)
        self._default_fn = o

    def _hex(self):
        """8 chars long hash of url for unique identity.
        :return: hash of the url
        """
        return hashlib.sha512(self.url.encode("UTF-8")).hexdigest()[:8]

    @property
    def url(self):
        """Final url generated after any base_url or original change actions.
        :rtype: str
        :return: url calculated using all the factors
        """
        if self.base_url:
            url = unquote(urljoin(self.base_url, self._url))
        else:
            url = unquote(self._url)
        # Fixes a bug in urljoin which leaves relative path notations
        # inside the joined urls
        url = RELATIVE_PATHS.sub('', url)
        return url

    @url.setter
    def url(self, u):
        if not isinstance(u, basestring):
            raise TypeError("Expected <%r>, got <%r>." % (basestring, type(u)))
        self._url = u

    @staticmethod
    def clean_url(url):
        """Cleans any url of relative paths remaining after urljoin.

        :param url: any url containing relative path contamination
        :type url: str
        :rtype: str
        :returns: cleaned url

        usage::
            >>> clean_url('http://google.com/../../url/path/#frag')
            'http://google.com/url/path/'
            >>> clean_url('../../url/path')
            'url/path'
            >>> clean_url('./same/dir/')
            'same/dir/'

        """
        return RELATIVE_PATHS.sub('', unquote(urldefrag(url)[0]))

    @staticmethod
    def clean_fn(file_path):
        """Removes any unwanted patterns or characters from filepath."""

        file_path = SPECIAL_CHARS.sub('', file_path)  # any unwanted char
        file_path = URL_FRAG.sub('', file_path)  # query strings
        file_path = RELATIVE_PATHS.sub('', file_path)  # relative paths

        return file_path

    @property
    def parsed_url(self):
        """Parses the url in six part tuple."""
        return urlsplit(self.clean_url(self.url))

    @property
    def hostname(self):
        # must return empty string in None cases
        return self.parsed_url.hostname or ''

    @property
    def port(self):
        """:rtype: int"""
        return self.parsed_url.port

    @property
    def url_path(self):
        return self.parsed_url.path

    @property
    def scheme(self):
        return self.parsed_url.scheme

    @property
    def base_url(self):
        """Absolute url this url if set.
        :rtype: str
        """
        return self._base_url

    @base_url.setter
    def base_url(self, new_base):
        """Set the parent url of this object to new new_base.

        :param str new_base: absolute url of the domain
        :rtype: None
        """
        if not isinstance(new_base, basestring):
            raise TypeError("Base url must be of string type!")
        self._base_url = new_base

    @property
    def base_path(self):
        """Returns the base path if set.
        :rtype: str
        """
        return self._base_path

    @base_path.setter
    def base_path(self, new_base_path):
        """Base file which would be prepended to the new path generated via url.

        ..version changed:: 6.0.0
            Added path normalising and type checks

        """
        if not isinstance(new_base_path, basestring):
            raise TypeError("Path must be of string type!")
        self._base_path = os.path.normpath(new_base_path) or ''

    @property
    def to_path(self):
        """Returns a file path made from url.

        :rtype: str
        :returns: path assumed from url
        """
        if self.base_path:
            return os.path.join(self.base_path, self._path_from_url())
        return self._path_from_url()

    def _path_from_url(self):
        """Returns a feasible path extracted from the url converted to disk style convention."""
        return os.path.normpath(url2pathname(self.clean_fn(self.hostname + self.url_path)))

    @property
    def file_name(self):
        """Returns a file name from url url_path.
        # Web pages can be displayed without any file name So a default
        # file name is required in case.
        :rtype: str
        :return: filename present in the url or default one
        """
        fn, pos = self.get_filename_and_pos(self.url_path)

        if not fn:
            return self.default_filename
        else:
            return fn

    @staticmethod
    def insert(string, new_object, index):
        """Inserts a new string at specified index in the basestring

        :param string: base string in which new fragment to be inserted
        :type string: str
        :param new_object: new fragment
        :type new_object: str
        :param index: position at which the fragment will be inserted in basestring
        :type index: int
        :return: new extended string
        :rtype: str
        """
        return string[index:] + new_object + string[:index]

    def get_filename_and_pos(self, path):
        """Finds the filename in a url and returns a tuple containing filename and position.

        :type path: str
        :param path: path in which to find the filename
        :rtype: tuple
        :return: two-tuple containing filename name its start position
        """

        fn = self.clean_fn(path)

        i = len(fn)  # pointer to the end of string
        # iter until first slash found and stop before it
        while i and fn[i - 1] not in '/\\':
            i -= 1
        fn = fn[i:]  # string slice present after the slash
        return fn, i

    def get_fileext_and_pos(self, path):
        """Finds the file extension in a url and returns a tuple containing extension and position.

        :type path: str
        :param path: path in which to find the extension
        :rtype: tuple
        :return: two-tuple containing filename name its start position
        """
        fn, _ = self.get_filename_and_pos(path)

        i = len(fn)  # pointer to the end of string
        # iter until first slash found and stop before it
        while i and fn[i - 1] != '.':
            i -= 1

        # no extension present
        if i == 0:
            return '', 0

        fe = fn[i:]
        return fe, len(path) - len(fn) + i

    def _refactor_filename(self, path, prefix=None, sep=None):
        """Refactors a filename in a path and modifies it according to need.

        NOTE : internal use only
        NOTE : specially designed for url addresses and not file addresses


        :param path: path from which the filename to be extracted
        :return: two-tuple containing refactored filename and its start position
        """
        if prefix:
            assert isinstance(prefix, basestring)
        else:
            prefix = str(self._hex())
        if sep:
            assert isinstance(sep, basestring)
        else:
            sep = '__'

        fn, pos = self.get_filename_and_pos(path)

        if fn:
            # new_fn = fn
            new_fn = prefix + sep + fn
        else:
            new_fn = self.default_filename

        if pos == 0:  # a slash does not exists in path
            new_fn = '/' + new_fn

        # make sure the files extension becomes required type
        fe, ext_pos = self.get_fileext_and_pos(new_fn)

        if ext_pos == 0:  # if not present then add a default file extension
            new_fn += '.' + self.default_suffix
        else:
            if self.enforce_suffix:  # if forced extension conversion is requested
                new_fn = new_fn[:ext_pos] + self.default_suffix

        # replace original filename with unique filename
        return path[:pos] + new_fn, pos

    @property
    def file_path(self):
        """Make a unique path from the url.

        :rtype: str
        :return: disk compatible path
        """
        path, _ = self._refactor_filename(self.url_path)
        hostname = self.hostname

        assert isinstance(path, basestring)
        assert isinstance(hostname, basestring)

        # clean the url and prepend hostname to make it complete
        path = url2pathname(hostname + path)

        if self.base_path:
            path = os.path.join(self.base_path, path)
        return path

    def relative_to(self, path):
        """
        Returns path relative to the given path.

        :param path: Path to which relative have to be generated
        """
        if not isinstance(path, basestring):
            raise TypeError

        path = os.path.normpath(path)
        start = os.path.dirname(path)

        head, tail = os.path.split(self.file_path)

        rel_path = os.path.relpath(head, start)

        return os.path.join(rel_path, tail)


def relate(target_file, start_file):
    """
    Returns relative path of target-file from start-file.
    """

    # Default os.path.rel_path takes directories as argument, thus we need strip the filename
    # if present in the path else continue as is.
    target_dir = os.path.dirname(target_file)
    start_dir = os.path.dirname(start_file)

    # Calculate the relative path using the standard module and then concatenate the file names if
    # they were previously present.
    return os.path.join(os.path.relpath(target_dir, start_dir), os.path.basename(target_file))
