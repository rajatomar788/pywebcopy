# -*- coding: utf-8 -*-

"""
aerwebcopy.structures
~~~~~~~~~~~~~~~~~~~~~

Data structures powering aerwebcopy.
"""

import collections
import os
import bs4

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

__all__ = [
    'CaseInsensitiveDict', 'WebPage'
]


class CaseInsensitiveDict(collections.MutableMapping):
    """Provides flexible dictionary which creates less errors
    during lookups.

    Source: `requests.structures`

    Examples:
        dict = CaseInsensitiveDict()
        dict['Config'] = 'Config'

        dict.get('config') => 'Config'
        dict.get('CONFIG') => 'Config'
        dict.get('conFig') => 'Config'
    """

    def __init__(self, data=None, **kwargs):
        self._store = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        # store the lowered case key along with original key
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (orig_key for orig_key, key_value in self._store.values())

    def __len__(self):
        return len(self._store)

    def lowered_case_items(self):
        return (
            (lowered_key, key_tuple[1])
            for lowered_key, key_tuple in self._store.items()
        )

    def __eq__(self, other):
        if isinstance(other, collections.Mapping):
            other = CaseInsensitiveDict(other)
        else:
            raise NotImplemented

        return dict(self.lowered_case_items()) == dict(other.lowered_case_items())

    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))


import core
import config
import utils
import generators


class WebPage(bs4.BeautifulSoup):
    """
    Represents a web page in python code.
    You can use any method of beautiful_soup and also
    save the web page with class methods easily

    :param url: url of the web page

    Example:
    
        wp = WebPage(url='http://google.com')
        wp.save_complete()

    """

    def __init__(self, url, *args, **kwargs):
        self.file_name = 'index.html' if 'index.html' not in url else ''
        self.url = urlparse.urljoin(url, self.file_name)
        self.file_path = os.path.join(config.config['mirrors_dir'], utils.compatible_path(url))
        self.request = core.get(self.url)
        super(WebPage, self).__init__(self.request.content, parser='html.parser', *args, **kwargs)

    def __repr__(self):
        return '<WebPage {}>'.format(self.url)

    def save_html_only(self):
        # directly save the file
        core.new_file(file_path=self.url, url=self.url)

    def save_complete(self):
        # save any css or js or images linked to this page
        generators.generate_style_map(file_url=self.url, file_soup=self)

        # convert the css and js links to a path relative to this file
        generators.generate_relative_paths(file_soup=self, file_path=self.file_path)

        # finally save the html page itself
        core.new_file(file_path=self.url, content=self)
