# -*- coding: utf-8 -*-

"""
pywebcopy.compat
~~~~~~~~~~~~~~~

This module handles import compatibility issues between Python 2 and
Python 3.
"""

import sys

_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)


# ---------
# Specifics
# ---------

if is_py2:
    from urllib import (
        quote, unquote, quote_plus, unquote_plus, urlencode,
        )
    from urlparse import urlparse, urlunparse, urljoin, urlsplit, urldefrag, url2pathname, pathname2url
    from robotparser import *

    builtin_str = str
    bytes = str
    str = unicode
    basestring = basestring
    numeric_types = (int, long, float)
    integer_types = (int, long)

elif is_py3:
    from urllib.parse import (urlparse, urlunparse, urljoin, urlsplit, urlencode,
        quote, unquote, quote_plus, unquote_plus, urldefrag)
    from urllib.request import url2pathname, pathname2url
    from io import BytesIO
    from collections import OrderedDict
    from urllib.robotparser import *
    builtin_str = str
    str = str
    bytes = bytes
    basestring = (str, bytes)
    numeric_types = (int, float)
    integer_types = (int,)
