# Copyright 2020; Raja Tomar
# See license for more details
#
# The main function `url2path` is optimised to be fast using caching.
# Here is a timeit result for the same.
#
# [IPython] timeit url2path("http://httpbin.org/bytes/1")
# 94.7 ns +- 26.5 ns per loop (mean +- std. dev. of 7 runs, 10000000 loops each)

import os
import re
from cgi import parse_header
from collections import namedtuple
from hashlib import md5
from zlib import adler32

from six import PY2
from six import text_type
from six import binary_type
from six import string_types
from six.moves.urllib.parse import unquote
from six.moves.urllib.parse import urljoin

from .helpers import lru_cache

__all__ = [
    'url2path', 'filename_present', 'relate', 'get_etag', 'HIERARCHY', 'LINEAR',
    'parse_url', 'parse_header', 'get_host', 'get_prefix', 'get_suffix',
    'Url', 'LocationParseError', 'secure_filename', 'split_first',
    'common_prefix_map', 'common_suffix_map', 'get_content_type_from_headers',
    'Context', 'ContextError',
]

url_attrs = ['scheme', 'auth', 'host', 'port', 'path', 'query', 'fragment']

# We only want to normalize urls with an HTTP(S) scheme.
# urllib3 infers URLs without a scheme (None) to be http.
NORMALIZABLE_SCHEMES = ('http', 'https', None)


class LocationParseError(ValueError):
    """Invalid url format."""


class Url(namedtuple('Url', url_attrs)):
    """
    Data structure for representing an HTTP URL. Used as a return value for
    :func:`parse_url`. Both the scheme and host are normalized as they are
    both case-insensitive according to RFC 3986.
    """
    __slots__ = ()

    def __new__(cls, scheme=None, auth=None, host=None, port=None, path=None,
                query=None, fragment=None):
        if path and not path.startswith('/'):
            path = '/' + path
        if scheme:
            scheme = scheme.lower()
        if host and scheme in NORMALIZABLE_SCHEMES:
            host = host.lower()
        # noinspection PyArgumentList
        return super(Url, cls).__new__(cls, scheme, auth, host, port, path,
                                       query, fragment)

    @property
    def hostname(self):
        """For backwards-compatibility with urlparse. We're nice like that."""
        return self.host

    @property
    def request_uri(self):
        """Absolute path including the query string."""
        uri = self.path or '/'

        if self.query is not None:
            uri += '?' + self.query

        return uri

    @property
    def netloc(self):
        """Network location including host and port"""
        if self.port:
            return '%s:%d' % (self.host, self.port)
        return self.host

    @property
    def url(self):
        """
        Convert self into a url

        This function should more or less round-trip with :func:`.parse_url`. The
        returned url may not be exactly the same as the url inputted to
        :func:`.parse_url`, but it should be equivalent by the RFC (e.g., urls
        with a blank port will have : removed).

        Example: ::

            >>> U = parse_url('http://google.com/mail/')
            >>> U.url
            'http://google.com/mail/'
            >>> Url('http', 'username:password', 'host.com', 80,
            ... '/path', 'query', 'fragment').url
            'http://username:password@host.com:80/path?query#fragment'
        """
        scheme, auth, host, port, path, query, fragment = self
        url = ''

        # We use "is not None" we want things to happen with empty strings (or 0 port)
        if scheme is not None:
            url += scheme + '://'
        if auth is not None:
            url += auth + '@'
        if host is not None:
            url += host
        if port is not None:
            url += ':' + str(port)
        if path is not None:
            url += path
        if query is not None:
            url += '?' + query
        if fragment is not None:
            url += '#' + fragment

        return url

    def __str__(self):
        return self.url


def split_first(s, delims):
    """
    Given a string and an iterable of delimiters, split on the first found
    delimiter. Return two split parts and the matched delimiter.

    If not found, then the first part is the full input string.

    Example::

        >>> split_first('foo/bar?baz', '?/=')
        ('foo', 'bar?baz', '/')
        >>> split_first('foo/bar?baz', '123')
        ('foo/bar?baz', '', None)

    Scales linearly with number of delims. Not ideal for large number of delims.
    """
    min_idx = None
    min_delim = None
    for d in delims:
        idx = s.find(d)
        if idx < 0:
            continue

        if min_idx is None or idx < min_idx:
            min_idx = idx
            min_delim = d

    if min_idx is None or min_idx < 0:
        return s, '', None

    return s[:min_idx], s[min_idx + 1:], min_delim


def parse_url(url):
    """
    Given a url, return a parsed :class:`.Url` namedtuple. Best-effort is
    performed to parse incomplete urls. Fields not provided will be None.

    Partly backwards-compatible with :mod:`urlparse`.

    Example::

        >>> parse_url('http://google.com/mail/')
        Url(scheme='http', host='google.com', port=None, path='/mail/', ...)
        >>> parse_url('google.com:80')
        Url(scheme=None, host='google.com', port=80, path=None, ...)
        >>> parse_url('/foo?bar')
        Url(scheme=None, host=None, port=None, path='/foo', query='bar', ...)
    """

    # While this code has overlap with stdlib's urlparse, it is much
    # simplified for our needs and less annoying.
    # Additionally, this implementations does silly things to be optimal
    # on CPython.

    if not url:
        # Empty
        return Url()

    scheme = None
    auth = None
    host = None
    port = None
    path = None
    fragment = None
    query = None

    # Scheme
    if '://' in url:
        scheme, url = url.split('://', 1)

    # Find the earliest Authority Terminator
    # (http://tools.ietf.org/html/rfc3986#section-3.2)
    url, path_, delim = split_first(url, ['/', '?', '#'])

    if delim:
        # Reassemble the path
        path = delim + path_

    # Auth
    if '@' in url:
        # Last '@' denotes end of auth part
        auth, url = url.rsplit('@', 1)

    # IPv6
    if url and url[0] == '[':
        host, url = url.split(']', 1)
        host += ']'

    # Port
    if ':' in url:
        _host, port = url.split(':', 1)

        if not host:
            host = _host

        if port:
            # If given, ports must be integers. No whitespace, no plus or
            # minus prefixes, no non-integer digits such as ^2 (superscript).
            if not port.isdigit():
                raise LocationParseError(url)
            try:
                port = int(port)
            except ValueError:
                raise LocationParseError(url)
        else:
            # Blank ports are cool, too. (rfc3986#section-3.2.3)
            port = None

    elif not host and url:
        host = url

    if not path:
        return Url(scheme, auth, host, port, path, query, fragment)

    # Fragment
    if '#' in path:
        path, fragment = path.split('#', 1)

    # Query
    if '?' in path:
        path, query = path.split('?', 1)

    return Url(scheme, auth, host, port, path, query, fragment)


def get_host(url):
    """
    Returns the Host info from the url.
    """
    p = parse_url(url)
    return p.scheme or 'http', p.hostname, p.port


def get_etag(string):
    if not isinstance(string, binary_type):
        string = string.encode()
    return md5(string).hexdigest()


def get_content_type_from_headers(headers, default=None):
    content_type = headers.get('Content-Type', default)
    if not content_type:
        return default
    content_type, params = parse_header(content_type)
    return content_type


# Pythons mime-types module is weird and does not specifies to web types.
# Here is the standard web mime-types list from mozilla website
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
common_suffix_map = {
    'application/epub+zip': '.epub',  # Electronic publication (EPUB)
    'application/javascript': '.js',  # JavaScript module
    'application/gzip': '.gz',  # GZip Compressed Archive
    'application/java-archive': '.jar',  # Java Archive (JAR)
    'application/json': '.json',  # JSON format
    'application/ld+json': '.jsonld',  # JSON-LD format
    'application/msword': '.doc',  # Microsoft Word
    'application/octet-stream': '.bin',  # Any kind of binary data
    'application/ogg': '.ogx',  # OGG
    'application/pdf': '.pdf',  # Adobe Portable Document Format (PDF)
    'application/php': '.php',  # Hypertext Preprocessor (Personal Home Page)
    'application/rtf': '.rtf',  # Rich Text Format (RTF)
    'application/vnd.amazon.ebook': '.azw',  # Amazon Kindle eBook format
    'application/vnd.apple.installer+xml': '.mpkg',  # Apple Installer Package
    'application/vnd.mozilla.xul+xml': '.xul',  # XUL
    'application/vnd.ms-excel': '.xls',  # Microsoft Excel
    'application/vnd.ms-fontobject': '.eot',  # MS Embedded OpenType fonts
    'application/vnd.ms-powerpoint': '.ppt',  # Microsoft PowerPoint
    'application/vnd.oasis.opendocument.presentation': '.odp',  # OpenDocument presentation document
    'application/vnd.oasis.opendocument.spreadsheet': '.ods',  # OpenDocument spreadsheet document
    'application/vnd.oasis.opendocument.text': '.odt',  # OpenDocument text document
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
    # Microsoft PowerPoint (OpenXML)
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',  # Microsoft Excel (OpenXML)
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',  # Microsoft Word (OpenXML)
    'application/vnd.rar': '.rar',  # RAR archive
    'application/vnd.visio': '.vsd',  # Microsoft Visio
    'application/x-7z-compressed': '.7z',  # 7-zip archive
    'application/x-abiword': '.abw',  # AbiWord document
    'application/x-bzip': '.bz',  # BZip archive
    'application/x-bzip2': '.bz2',  # BZip2 archive
    'application/x-csh': '.csh',  # C-Shell script
    'application/x-freearc': '.arc',  # Archive document (multiple files embedded)
    'application/x-sh': '.sh',  # Bourne shell script
    'application/x-shockwave-flash': '.swf',  # Small web format (SWF) or Adobe Flash document
    'application/x-tar': '.tar',  # Tape Archive (TAR)
    'application/xhtml+xml': '.xhtml',  # XHTML
    'application/xml': '.xml',  # XML
    'text/xml': '.xml',  # XML
    'application/zip': '.zip',  # ZIP archive
    'audio/aac': '.aac',  # AAC audio
    'audio/midi': '.mid',  # Musical Instrument Digital Interface (MIDI)
    'audio/x-midi': '.midi',  # Musical Instrument Digital Interface (MIDI)
    'audio/mpeg': '.mp3',  # MP3 audio
    'audio/ogg': '.oga',  # OGG audio
    'audio/opus': '.opus',  # Opus audio
    'audio/wav': '.wav',  # Waveform Audio Format
    'audio/webm': '.weba',  # WEBM audio
    'font/otf': '.otf',  # OpenType font
    'font/ttf': '.ttf',  # TrueType Font
    'font/woff': '.woff',  # Web Open Font Format (WOFF)
    'font/woff2': '.woff2',  # Web Open Font Format (WOFF)
    'image/bmp': '.bmp',  # Windows OS/2 Bitmap Graphics
    'image/gif': '.gif',  # Graphics Interchange Format (GIF)
    'image/jpeg': '.jpeg',  # JPEG images
    'image/jpg': '.jpg',  # JPG images
    'image/png': '.png',  # Portable Network Graphics
    'image/svg+xml': '.svg',  # Scalable Vector Graphics (SVG)
    'image/tiff': '.tiff',  # Tagged Image File Format (TIFF)
    'image/x-icon': '.ico',  # Icon format
    'image/vnd.microsoft.icon': '.ico',  # Icon format
    'image/webp': '.webp',  # WEBP image
    'text/calendar': '.ics',  # iCalendar format
    'text/css': '.css',  # Cascading Style Sheets (CSS)
    'text/csv': '.csv',  # Comma-separated values (CSV)
    'text/html': '.html',  # HyperText Markup Language (HTML)
    'text/javascript': '.mjs',  # JavaScript module',
    'text/plain': '.txt',  # Text, (generally ASCII or ISO 8859-n)',
    "video/3gpp": '.3gp',  # 3GPP audio/video container',
    "audio/3gpp": '.3gp',  # 3GPP audio/video container',
    "video/3gpp2": '.3g2',  # 3GPP2 audio/video container'
    "audio/3gpp2": '.3g2',  # 3GPP2 audio/video container'
    'video/mp2t': '.ts',  # MPEG transport stream
    'video/mpeg': '.mpeg',  # MPEG Video
    'video/ogg': '.ogv',  # OGG video
    'video/webm': '.webm',  # WEBM video
    'video/x-msvideo': '.avi'  # AVI: Audio Video Interleave
}


def get_suffix(content_type):
    return common_suffix_map.get(content_type)


# common file names for some web file types.
common_prefix_map = {
    'application/javascript': 'app',
    'application/json': 'data',
    'application/octet-stream': 'binary',
    'image/gif': 'gif',
    'image/jpeg': 'image',
    'image/x-icon': 'favicon',
    'text/css': 'style',
    'text/html': 'index',
    'text/plain': 'text'
}


def get_prefix(content_type):
    return common_prefix_map.get(content_type)


HIERARCHY = 'HIERARCHY'
LINEAR = 'LINEAR'

# Helpers for bytes handling
_implicit_encoding = 'ascii'
_implicit_errors = 'ignore'


def _encode_result(obj, encoding=_implicit_encoding,
                   errors=_implicit_errors):
    return obj.encode(encoding, errors)


def _decode_args(args, encoding=_implicit_encoding,
                 errors=_implicit_errors):
    return tuple(x.decode(encoding, errors) if x else '' for x in args)


def _coerce_args(*args):
    # Invokes decode if necessary to create str args
    # and returns the coerced inputs along with
    # an appropriate result coercion function
    #   - noop for str inputs
    #   - encoding function otherwise
    str_input = isinstance(args[0], text_type)
    for arg in args[1:]:
        # We special-case the empty string to support the
        # "scheme=''" default argument to some functions
        if arg and isinstance(arg, text_type) != str_input:
            raise TypeError("Cannot mix str and non-str arguments")
    if str_input:
        return args + (lambda x: x,)
    return _decode_args(args) + (_encode_result,)


_windows_device_files = frozenset(
        ['CON', 'PRN', 'AUX', 'NUL'] +
        ['COM%d' % i for i in range(1, 10)] +
        ['LPT%d' % i for i in range(1, 10)]
)

_filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]+')


def secure_filename(filename, sub='_'):
    if isinstance(filename, text_type):
        from unicodedata import normalize
        filename = normalize('NFKD', filename).encode(
            _implicit_encoding, _implicit_errors)
        if not PY2:
            filename = filename.decode(_implicit_encoding)
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    filename = str(_filename_ascii_strip_re.sub(sub, '_'.join(
        filename.split()))).strip('._')

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if os.name == 'nt' and filename and \
            filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename

    return filename


def _filter_and_group_segments(url, remove_query=True, remove_frag=True):
    """
    Groups the parts in a base and tail fashion.

    ..usage::
        >>> s = 'http://www.nx-domain.com/blog/index?q=query#fragment'
        >>> _filter_and_group_segments(s, remove_query=True, remove_frag=True)
        >>> (('www.nx-domain.com', 'blog'), 'index')
        >>> _filter_and_group_segments(s, remove_query=False, remove_frag=True)
        >>> (('www.nx-domain.com', 'blog'), 'index_q_query')
        >>> _filter_and_group_segments(s, remove_query=False, remove_frag=False)
        >>> (('www.nx-domain.com', 'blog'), 'index_q_query_fragment')

    :param str url: url of which parts are to be processed
    :param bool remove_query: whether to remove the query parameters from url.
    :param bool remove_frag: whether to remove the fragment parameters from url.
    :rtype: tuple
    :return: grouped parts
    """
    scheme, auth, host, port, path, query, fragment = parse_url(unquote(url))

    host = (secure_filename(host),) if isinstance(host, string_types) and host != '' else tuple()
    path = path if isinstance(path, string_types) else ''
    segments = path.lstrip('/').split('/')

    base = host + tuple(secure_filename(i) for i in segments[:-1])
    leaf = secure_filename(segments[-1])
    stem, ext = os.path.splitext(leaf)
    if not remove_query and isinstance(query, string_types):
        stem = '_'.join(filter(None, (stem, secure_filename(query))))
    if not remove_frag and isinstance(fragment, string_types):
        stem = '_'.join(filter(None, (stem, secure_filename(fragment))))
    return base, stem, ext


def _url2path(url,
              base_url=None,
              etag=None,
              remove_query=None,
              remove_frag=None,
              prefix=None,
              suffix=None,
              prefix_errors=None,
              suffix_errors=None):
    if not isinstance(url, string_types):
        raise TypeError('Expected url of type %r, got %r' % (string_types, url))
    if isinstance(base_url, string_types):
        url = urljoin(base_url, url)

    base, stem, ext = _filter_and_group_segments(
        url, remove_query, remove_frag)

    if prefix and isinstance(prefix, string_types):
        if prefix_errors == 'append':
            stem = '_'.join(filter(None, (prefix, stem)))
        elif prefix_errors == 'replace':
            stem = prefix
        else:
            if not stem:
                stem = prefix

    if not stem or etag:
        if not isinstance(etag, string_types):
            etag = str(adler32(url.encode(_implicit_encoding, _implicit_errors)))
        stem = '.'.join(filter(None, (stem, etag)))

    if suffix and isinstance(suffix, string_types):
        # avoid appending if it is equal to existing ext.
        if suffix_errors == 'append' and ext != suffix:
            ext = ''.join(filter(None, (ext, suffix)))
        elif suffix_errors == 'replace':
            ext = suffix
        else:
            if not ext:
                ext = suffix
    return tuple(base), ''.join((stem, ext))


@lru_cache()
def url2path(url,
             base_url=None,
             base_path=None,
             tree_type=HIERARCHY,
             etag=None,
             remove_query=None,
             remove_frag=None,
             prefix=None,
             suffix=None,
             prefix_errors=None,
             suffix_errors=None):
    """Automated disk path generator for urls.

    The urls not always contain a proper filename at which
    the file could be saved i.e. 'http://httpbin.org/bytes/10'.
    To deal with these kind of binary streams retrieving,
    a automated name generator is used which at its core
    usage the `hashes` to create unique non repeating names.

    Simple workaround to convert the urls into paths.
    Joins the url with a base url and then transforms the
    url into a disk-path or file-path with added base path.
    It returns a generated path along with the name and
    hex digest of the joined absolute url.

    Tree types:-
        let there be two paths *"/subdir1/file1"* and *"/file2"*

        linear:-
            basedir/
                    file1
                    file2
        hierarchy:-
            basedir/
                subdir1/
                    file1
                file2

    ..features::
        1. base url joining and normalisations
        2. basename generation if not present
        3. pure disk compatible path
        4. additional base path joining
        5. prefix and suffix implicit support
        6. Tree types: linear or hierarchy

    ..usage::
        >>> url2path('http://nx-domain.com/path/to/file?q=value')
        >>> r'nx-domain.com\\path\\to\\file_q_value'

    """
    url, base_url, base_path, prefix, suffix, _encode = _coerce_args(
        url, base_url, base_path, prefix, suffix)

    dirname, basename = _url2path(
        url, base_url, etag, remove_query, remove_frag,
        prefix, suffix, prefix_errors, suffix_errors)

    if isinstance(base_path, string_types) and '~' in base_path:
        base_path = os.path.expanduser(base_path)

    # hierarchy or a linear tree
    if tree_type == LINEAR:
        if isinstance(base_path, string_types):
            path = os.path.join(base_path, basename)
        else:
            path = basename
    else:
        if isinstance(base_path, string_types):
            path = os.path.join(base_path, *(dirname + (basename,)))
        else:
            path = os.path.join(*(dirname + (basename,)))
    return _encode(os.path.normpath(path))


def from_content_type(response, base_url=None, base_path=None, tree_type=HIERARCHY):
    """Builds the path for the url from a http response.

    :type response: requests.Response or urllib.Response
    :type base_url: string_types
    :type base_path: string_types
    :type tree_type: LINEAR or HIERARCHY
    :rtype: string_types
    :return: calculated path
    """
    assert hasattr(response, 'headers'), "Response object must have a 'headers' attribute!"
    assert hasattr(response, 'url'), "Response object must have a 'url' attribute!"
    ctypes = get_content_type_from_headers(response.headers)
    return url2path(
        url=response.url,
        base_url=base_url,
        base_path=base_path,
        tree_type=tree_type,
        prefix=get_prefix(ctypes),
        suffix=get_suffix(ctypes)
    )


def relate(target_file, start_file):
    """
    Returns relative path of target-file from start-file.
    """
    # Default os.path.rel_path takes directories as argument, thus we need
    # strip the filename if present in the paths else continue as is.
    target_dir, target_base = os.path.split(target_file)
    start_dir = os.path.dirname(start_file)

    # Calculate the relative path using the standard module and then concatenate
    # the file names if  they were previously present.
    return os.path.join(os.path.relpath(target_dir, start_dir), target_base)


def filename_present(url):
    """Checks whether a `filename` is present in the url/path or not.

    :param str url: url string to check the file name in.
    :return boolean: True if present, else False
    """
    return bool(_filter_and_group_segments(url, remove_query=True, remove_frag=True)[1])


context_attrs = [
    'url', 'base_url', 'base_path', 'tree_type', 'content_type',
]


class ContextError(AttributeError):
    """Bad context attribute or operation."""


class Context(namedtuple('Context', context_attrs)):
    __slots__ = ()

    @classmethod
    def from_config(cls, config):
        url = config.get('project_url')
        path = config.get('project_folder')
        tree_type = config.get('tree_type')
        if None in (url, path, tree_type):
            raise AttributeError("Values can't be NoneType.", url, path, tree_type)
        return cls(url, url, path, tree_type, None)

    def __new__(cls, url=None, base_url=None, base_path=None, tree_type=None, content_type=None, **kwargs):
        if tree_type not in (LINEAR, HIERARCHY):
            raise ValueError("TreeType should be either LINEAR or HIERARCHY.")

        if not isinstance(url, string_types):
            raise TypeError(url)

        if base_url and not isinstance(base_url, string_types):
            raise TypeError(base_url)
        if base_url is None:
            base_url = url

        if not isinstance(base_path, string_types):
            raise TypeError(base_path)
        base_path = os.path.normpath(base_path)

        # noinspection PyArgumentList
        return super(Context, cls).__new__(cls, url, base_url, base_path, tree_type, content_type)

    def with_values(self, **kwargs):
        return self._replace(**kwargs)

    def create_new_from_url(self, url):
        """Creates a new identical context with only difference of the url."""
        #: The base url for the new url should be the url of the parent context
        #: and not the absolute parent url. Learned a lesson today!
        return self.with_values(url=urljoin(self.url, url), content_type=None)

    def resolve(self):
        prefix = suffix = None
        if self.content_type is not None:
            prefix = get_prefix(self.content_type)
            suffix = get_suffix(self.content_type)

        return url2path(
            url=self.url,
            base_url=self.base_url,
            base_path=self.base_path,
            tree_type=self.tree_type,
            prefix=prefix, suffix=suffix,
            suffix_errors='append'
        )
