# -*- coding: utf-8 -*-
"""
pywebcopy.crawler
~~~~~~~~~~~~~~~~~

Crawls a specific url and saves any internal pages found.

usage::
    >>> from pywebcopy import config, Crawler
    >>> url = 'https://google.com'
    >>> project_folder = '/path/to/downloads/'
    >>> project_name = 'google_clone'
    >>> kwargs = {'bypass_robots': True}
    >>> config.setup_config(url, project_folder, project_name, **kwargs)
    >>> crawler = Crawler(url)
    >>> crawler.run()

"""
import os
import threading
import warnings

from .elements import TagBase
from .parsers import Parser
from .webpage import WebPage


INDEX = set()
INDEX_LOCK = threading.Lock()


class SubPage(TagBase):
    """Custom anchor tag handler.
    This creates a WebPage objects directly and can start it.
    Replaces the generated web page objects transformer by itself
    so that the path generation depends on this instead of WebPage object.
    The apis of a tag handler are still same thus it is easy
    to be handled by the parser internally.
    """

    sub_handler = WebPage
    eMap = {}

    __slots__ = '_sub_page',

    def __init__(self, *args, **kwargs):
        super(SubPage, self).__init__(*args, **kwargs)
        self.default_stem = 'index'
        self.default_suffix = 'html'
        self.enforce_suffix = True
        self._sub_page = None

    def _get_sub_page(self):
        if self._sub_page is not None:
            if isinstance(self._sub_page, (WebPage, Parser)):
                if not getattr(self._sub_page, '_url_obj'):
                    self._sub_page.utx = self
                if not getattr(self._sub_page, '_source'):
                    self._sub_page.get(self.url)
                if not getattr(self._sub_page, '_parseComplete'):
                    self._sub_page.parse()
            else:
                raise TypeError(
                    "Unknown SubPage handler! Expected <%r>, got <%r>."
                    % (WebPage, type(self._sub_page))
                )
        else:
            obj = object.__new__(self.sub_handler)
            obj.__init__()
            if self.eMap and isinstance(self.eMap, dict):
                obj._element_map = self.eMap
            #: overriding the properties of WebPage object with the
            #: properties from this transformer object
            obj.utx = self
            self._sub_page = obj
            obj.get(self.url)
            obj.parse()

        return self._sub_page

    def run(self):
        """Creates a WebPage object to download the page at the url.

        :rtype: WebPage
        :returns : used webpage
        """
        if not self.url.startswith(self.base_url) or \
                os.path.exists(self.file_path):
            return

        _sub_page = self._get_sub_page()

        if _sub_page is None or not getattr(_sub_page, '_stack'):
            return

        with INDEX_LOCK:
            elements = list(_sub_page.elements)
            for elem in elements:
                if elem.url not in INDEX:
                    INDEX.add(elem.url)
                else:
                    _sub_page.elements.remove(elem)

        _sub_page.save_complete()

        return _sub_page


class Crawler(WebPage):
    """Crawls a specific url and saves any internal pages found.

    Usage::
        >>> from pywebcopy import config, Crawler
        >>> url = 'http://some-site.com/'
        >>> project_folder = '/home/users/me/download_folder/site_clones/'
        >>> project_name = 'my_project'
        >>> kwargs = {'bypass_robots': True}
        >>> config.setup_config(url, project_folder, project_name, **kwargs)
        >>> crawler = Crawler(url)
        >>> crawler.run()

    :type url: str
    :param url: url of the website to clone
    """
    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)

        if 'scan_level' in kwargs:
            warnings.warn(
                "The scan_level setting has been deprecated and"
                "is now not supported. Thus leave it as is."
            )

        wrapper = SubPage
        setattr(wrapper, 'eMap', self._element_map)
        self.register_tag_handler('a', wrapper)
        self.register_tag_handler('form', wrapper)

    def run(self):
        """
        Asserts all the parameters required and then invokes the
        parsing and download process.
        """
        assert self.url is not None, "Url not setup."
        assert self.path is not None, "Folder path not setup."

        #: Fill the data and start
        if not self._source:
            self.get(self.url)

        self.parse()

        with INDEX_LOCK:
            elements = list(self.elements)
            for elem in elements:
                INDEX.add(elem.url)

        self.save_complete()

        # Remember the file path where the file is going to be saved
        # to let the further ease of pop open a browser with this
        # address
        # setattr(self, 'file_path', self.utx.file_path)

    crawl = run
