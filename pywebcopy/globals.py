# -*- coding: utf-8 -*-

import re
import textwrap

from . import __version__


VERSION = "v%d.%d.%d %s %d" % __version__

MARK = textwrap.dedent("""
        {0}
        * AerWebCopy Engine [version {1}]
        * Copyright Aeroson Systems & Co.
        * File mirrored from {2}
        * At UTC time: {3}
        {4}
        """)


CSS_URLS_RE = re.compile(b'''url\\(['"]?([^)]*)["']?\\)''', re.I)
"""Matches any url() declaration in a css file."""

CSS_IMPORTS_RE = re.compile(b'''@import\\s*['"](.*?)['"]\\s*''', re.I)
"""Matches any @import declaration in a css file."""

CSS_FILES_RE = re.compile(b'''(?:url\\(['"]?([^)]*)["']?\\))|(?:@import\\s*['"](.*?)['"]\\s*)''', re.I)
"""Both urls and imports combined."""

DATA_URL_RE = re.compile(r'^data:image/.+;base64', re.I)
"""Matches any base64 encoded image data url."""

"""Attributes which only contains single link."""
SINGLE_LINK_ATTRIBS = frozenset([
    'action', 'archive', 'background', 'cite', 'classid',
    'codebase', 'data', 'href', 'longdesc', 'profile', 'src',
    'usemap',
    # Not standard:
    'dynsrc', 'lowsrc',
    # Extras
    'data-src',
    ])

LIST_LINK_ATTRIBS = frozenset([
    'srcset', 'data-srcset'
])


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
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64;"
                  "PyWebcopyBot/{};)"
                  "AppleWebKit/604.1.38 (KHTML, like Gecko) "
                  "Chrome/68.0.3325.162".format(VERSION),
}
