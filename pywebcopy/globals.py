# -*- coding: utf-8 -*-
import os
import re
import textwrap
import threading

from . import __version__

# This makes sure the number of thread working remains
# under control so that the resource overloading could
# be prevented and the program remains memory efficient
#: new in version: 6.0.0
POOL_LIMIT = threading.Semaphore((os.cpu_count() or 1) * 4)

MARK = textwrap.dedent("""
        {0}
        * AerWebCopy Engine [version {1}]
        * Copyright Aeroson Systems & Co.
        * File mirrored from {2}
        * At UTC time: {3}
        {4}
        """)

# Fix: Issue of %22 being added at the end of urls.
# cause: alternating quotation marks should be dealt with.
# ISSUE #19 https://github.com/rajatomar788/pywebcopy/issues/19

"""Matches any url() declaration in a css file."""
# https://www.regextester.com/106463
# CSS_URLS_RE = re.compile(b'''url\(['"]?([^)])["']?\)''', re.I)
CSS_URLS_RE = re.compile(rb'''url\((?!['"]?(?:https?:|//))(['"]?)([^'")])\1\)''', re.I)

"""Matches any @import declaration in a css file."""
# https://regex101.com/r/lC1hO3/2
# CSS_IMPORTS_RE = re.compile(b'''@import\s*'"['"]\s*''', re.I)
CSS_IMPORTS_RE = re.compile(rb'''@import.?"'["'].?''', re.I)

"""Both urls and imports combined."""
# CSS_FILES_RE = re.compile(rb'''(?:url\((?!['"]?(?:https?:|//))(['"]?)([^'")])\1\))|(?:@import.?"'["'].*?)''', re.I)

# CSS_URLS_RE = re.compile(b'''url\\(['"]?([^)]*)["']?\\)''', re.I)
# CSS_IMPORTS_RE = re.compile(b'''@import\\s*['"](.*?)['"]\\s*''', re.I)
CSS_FILES_RE = re.compile(b'''(?:url\\(['"]?([^)"']*)["']?\\))|(?:@import\\s*['"](.*?)['"]\\s*)''', re.I)


DATA_URL_RE = re.compile(r'^data:image/.+;base64', re.I)
"""Matches any base64 encoded image data url."""

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

SINGLE_LINK_ATTRIBS = frozenset([
    'action', 'archive', 'background', 'cite', 'classid',
    'codebase', 'data', 'href', 'longdesc', 'profile', 'src',
    'usemap',
    # Not standard:
    'dynsrc', 'lowsrc',
    # Extras
    'data-src',
])
"""Attributes which only contains single link."""

LIST_LINK_ATTRIBS = frozenset([
    'srcset', 'data-srcset', 'src-set'
])
"""Attributes which contains multiple links."""

safe_file_exts = [
    '.html',
    '.php',
    '.asp',
    '.aspx',
    '.htm',
    '.xhtml',
    '.css',
    '.json',
    '.js',
    '.xml',
    '.svg',
    '.gif',
    '.ico',
    '.jpeg',
    '.pdf',
    '.jpg',
    '.png',
    '.ttf',
    '.eot',
    '.otf',
    '.woff',
    '.woff2',
    '.pwcf',  #: Default file extension
]

safe_http_headers = {
    "Accept-Language": "en-US,en;q=0.9",
    'User-Agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) "
        "Gecko/20100101 Firefox/70.0 PyWebCopyBot/{0}".format(__version__),
}
