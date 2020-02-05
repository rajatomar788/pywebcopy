# -*- coding: utf-8 -*-
import re
import textwrap
import threading

from . import __version__

import time
import functools
import collections

def lru_cache(maxsize = 255, timeout = None):
    """lru_cache(maxsize = 255, timeout = None) --> returns a decorator which returns an instance (a descriptor).

        Purpose         - This decorator factory will wrap a function / instance method and will supply a caching mechanism to the function.
                            For every given input params it will store the result in a queue of maxsize size, and will return a cached ret_val
                            if the same parameters are passed.

        Params          - maxsize - int, the cache size limit, anything added above that will delete the first values enterred (FIFO).
                            This size is per instance, thus 1000 instances with maxsize of 255, will contain at max 255K elements.
                        - timeout - int / float / None, every n seconds the cache is deleted, regardless of usage. If None - cache will never be refreshed.

        Notes           - If an instance method is wrapped, each instance will have it's own cache and it's own timeout.
                        - The wrapped function will have a cache_clear variable inserted into it and may be called to clear it's specific cache.
                        - The wrapped function will maintain the original function's docstring and name (wraps)
                        - The type of the wrapped function will no longer be that of a function but either an instance of _LRU_Cache_class or a functool.partial type.

        On Error        - No error handling is done, in case an exception is raised - it will permeate up.
    """

    class _LRU_Cache_class(object):
        def __init__(self, input_func, max_size, timeout):
            self._input_func        = input_func
            self._max_size          = max_size
            self._timeout           = timeout

            # This will store the cache for this function, format - {caller1 : [OrderedDict1, last_refresh_time1], caller2 : [OrderedDict2, last_refresh_time2]}.
            #   In case of an instance method - the caller is the instance, in case called from a regular function - the caller is None.
            self._caches_dict        = {}

        def cache_clear(self, caller = None):
            # Remove the cache for the caller, only if exists:
            if caller in self._caches_dict:
                del self._caches_dict[caller]
                self._caches_dict[caller] = [collections.OrderedDict(), time.time()]

        def __get__(self, obj, objtype):
            """ Called for instance methods """
            return_func = functools.partial(self._cache_wrapper, obj)
            return_func.cache_clear = functools.partial(self.cache_clear, obj)
            # Return the wrapped function and wraps it to maintain the docstring and the name of the original function:
            return functools.wraps(self._input_func)(return_func)

        def __call__(self, *args, **kwargs):
            """ Called for regular functions """
            return self._cache_wrapper(None, *args, **kwargs)
        # Set the cache_clear function in the __call__ operator:
        __call__.cache_clear = cache_clear


        def _cache_wrapper(self, caller, *args, **kwargs):
            # Create a unique key including the types (in order to differentiate between 1 and '1'):
            kwargs_key = "".join(map(lambda x : str(x) + str(type(kwargs[x])) + str(kwargs[x]), sorted(kwargs)))
            key = "".join(map(lambda x : str(type(x)) + str(x) , args)) + kwargs_key

            # Check if caller exists, if not create one:
            if caller not in self._caches_dict:
                self._caches_dict[caller] = [collections.OrderedDict(), time.time()]
            else:
                # Validate in case the refresh time has passed:
                if self._timeout != None:
                    if time.time() - self._caches_dict[caller][1] > self._timeout:
                        self.cache_clear(caller)

            # Check if the key exists, if so - return it:
            cur_caller_cache_dict = self._caches_dict[caller][0]
            if key in cur_caller_cache_dict:
                return cur_caller_cache_dict[key]

            # Validate we didn't exceed the max_size:
            if len(cur_caller_cache_dict) >= self._max_size:
                # Delete the first item in the dict:
                cur_caller_cache_dict.popitem(False)

            # Call the function and store the data in the cache (call it with the caller in case it's an instance function - Ternary condition):
            cur_caller_cache_dict[key] = self._input_func(caller, *args, **kwargs) if caller != None else self._input_func(*args, **kwargs)
            return cur_caller_cache_dict[key]


    # Return the decorator wrapping the class (also wraps the instance to maintain the docstring and the name of the original function):
    return (lambda input_func : functools.wraps(input_func)(_LRU_Cache_class(input_func, maxsize, timeout)))

# This makes sure the number of thread working remains
# under control so that the resource overloading could
# be prevented and the program remains memory efficient
#: new in version: 6.0.0
POOL_LIMIT = threading.Semaphore(5)

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
CSS_URLS_RE = re.compile(('url\((' + '["][^"]*["]|' + "['][^']*[']|" + '[^)]*)\)').encode(), re.I)

"""Matches any @import declaration in a css file."""
# https://regex101.com/r/lC1hO3/2
# CSS_IMPORTS_RE = re.compile(b'''@import\s*'"['"]\s*''', re.I)
CSS_IMPORTS_RE = re.compile(('@import "(.*?)"').encode())

"""Both urls and imports combined."""
# CSS_FILES_RE = re.compile(rb'''(?:url\((?!['"]?(?:https?:|//))(['"]?)([^'")])\1\))|(?:@import.?"'["'].*?)''', re.I)

# CSS_URLS_RE = re.compile(b'''url\\(['"]?([^)]*)["']?\\)''', re.I)
# CSS_IMPORTS_RE = re.compile(b'''@import\\s*['"](.*?)['"]\\s*''', re.I)
# XXX Not Needed
# CSS_FILES_RE = re.compile(b'''(?:url\\(['"]?([^)"']*)["']?\\))|(?:@import\\s*['"](.*?)['"]\\s*)''', re.I)


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
