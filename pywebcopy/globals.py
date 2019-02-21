# -*- coding: utf-8 -*-

import re
import sys
import textwrap

from . import __version__

PY2 = True if sys.version_info.major == 2 else False
PY3 = True if sys.version_info.major == 3 else False

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

DATA_URL_RE = re.compile(r'^data:image/.+;base64', re.I)
"""Matches any base64 encoded image data url."""

"""Attributes which only contains single link."""
SINGLE_LINK_ATTRIBS = frozenset([
    'action', 'archive', 'background', 'cite', 'classid',
    'codebase', 'data', 'href', 'longdesc', 'profile', 'src', 'data-src',
    'usemap',
    # Not standard:
    'dynsrc', 'lowsrc',
    ])

LIST_LINK_ATTRIBS = frozenset([
    'srcset', 'data-srcset'
])
