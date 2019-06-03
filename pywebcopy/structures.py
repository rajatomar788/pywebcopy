# -*- coding: utf-8 -*-

"""
pywebcopy.structures
~~~~~~~~~~~~~~~~~~~~

Structures powering pywebcopy.

"""

from collections import MutableMapping

import requests
from .compat import OrderedDict, RobotFileParser


__all__ = ['CaseInsensitiveDict', 'RobotsTxtParser']


class CaseInsensitiveDict(MutableMapping):
    """ Flexible dictionary which creates less errors
    during lookups.

    Examples:
        dict = CaseInsensitiveDict()
        dict['Config'] = 'Config'

        dict.get('config') => 'Config'
        dict.get('CONFIG') => 'Config'
        dict.get('conFig') => 'Config'
    """

    def __init__(self, data=None, **kwargs):
        self._store = OrderedDict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        self._store[key.lower()] = value

    def set(self, k, v):
        self.__setitem__(k, v)

    def __getitem__(self, key):
        return self._store[key.lower()]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (key for key, value in self._store.items())

    def __len__(self):
        return len(self._store)

    def __copy__(self):
        return CaseInsensitiveDict(self._store)

    def lower_case_items(self):
        return (
            (key.lower(), value) for key, value in self._store.items()
        )

    def __eq__(self, other):
        if isinstance(other, MutableMapping):
            other = CaseInsensitiveDict(other)
        else:
            raise NotImplementedError

        return dict(self.lower_case_items()) == dict(other.lower_case_items())


class RobotsTxtParser(RobotFileParser):
    """Reads the robots.txt from the site.

    Usage::
        >>> rp = RobotsTxtParser(user_agent='*', url='http://some-site.com/robots.txt')
        >>> rp.read()
        >>> rp.can_fetch('/hidden/url_path')
        >>> False
        >>> rp.can_fetch('/public/url_path/')
        >>> True

    """
    user_agent = '*'
    _get = None

    def set_ua(self, ua):
        self.user_agent = ua

    def read(self):
        """Modify the read method to use the inbuilt http session instead
        of using a new raw urllib connection.

        This usually sets up a session and a cookie jar.
        Thus subsequent requests should be faster.
        """
        try:
            f = self._get(self.url)
            f.raise_for_status()
        except requests.exceptions.HTTPError as err:
            code = err.response.status_code
            if code in (401, 403):
                self.disallow_all = True
            elif 400 <= code < 500:
                self.allow_all = True
        except requests.exceptions.ConnectionError:
            self.allow_all = True
        else:
            self.parse(f.text.splitlines())

    def can_fetch(self, url, user_agent=None):
        return super(RobotsTxtParser, self).can_fetch(user_agent or self.user_agent, url)
