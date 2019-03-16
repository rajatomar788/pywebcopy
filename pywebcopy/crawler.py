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

import warnings

from . import parsers
from .webpage import WebPage
from .elements import TagBase, LinkTag, ScriptTag, ImgTag
from .exceptions import PywebcopyError


class UrlAlreadyDownloaded(PywebcopyError):
    """The web page is already downloaded."""


class AnchorTagHandler(TagBase):
    """Custom anchor tag handler.
    This creates a WebPage objects directly and can start it.
    Replaces the generated web page objects transformer by itself
    so that the path generation depends on this instead of WebPage object.
    The apis of a tag handler are still same thus it is easy
    to be handled by the parser internally.
    """

    parser = WebPage

    def __init__(self, url, *args, **kwargs):
        TagBase.__init__(self, url=url, *args, **kwargs)

        self.default_filename = 'index.html'
        self.default_fileext = 'html'
        self.check_fileext = True

    def run(self):

        _sub_page = self.parser()

        #: overriding the properties of WebPage object with the
        #: properties from this transformer object
        _sub_page._url_obj = self
        _sub_page.url = self.url
        _sub_page.get(self.url)
        _sub_page.__parse__()
        _sub_page.save_complete()

        del _sub_page


def _with_parser(klass, parser):
    assert issubclass(klass, object), "First argument must be a Class!"
    assert issubclass(parser, object), "Second argument must be a Class!"

    setattr(klass, 'parser', parser)
    return klass


class Crawler(object):
    """Crawls a specific url and saves any internal pages found.

    Usage::
        >>> from pywebcopy import config, Crawler
        >>> url = 'http://some-site.com/'
        >>> project_folder = '/home/users/me/download_folder/site_clones/'
        >>> project_name = 'some_recognisable_name'
        >>> kwargs = {'bypass_robots': True}
        >>> config.setup_config(url, project_folder, project_name, **kwargs)
        >>> crawler = Crawler(url)
        >>> crawler.run()

    :type url: str
    :param url: url of the website to clone
    """

    def __init__(self, base_url, parser=None, **kwargs):
        if 'scan_level' in kwargs:
            warnings.warn("The scan_level setting has been deprecated and"
                          "is now not supported. Thus leave it as is.")

        if parser is None:
            self._parser = WebPage
        else:
            if not isinstance(parser, WebPage):
                TypeError("You need to pass the class, not a instance of it.")
            if not issubclass(parser, WebPage):
                TypeError("Parser is not of valid type!")

            self._parser = parser

        self.url = base_url

    def run(self):
        """Starts the chain reaction."""

        wrapper = AnchorTagHandler
        setattr(wrapper, 'parser', self._parser)

        # Recreate the element map
        parsers.element_map = {
            'link'  : LinkTag,
            'style' : LinkTag,
            'script': ScriptTag,
            'img'   : ImgTag,

            'a'     : wrapper,
            'form'  : wrapper,
        }
        #: Prepare a fresh web page object
        wp = self._parser()

        #: Fill the data and start
        wp.get(self.url)
        wp.save_complete()

        # Remember the file path where the file is going to be saved
        # to let the further ease of pop open a browser with this
        # address
        setattr(self, 'file_path', wp.utx.file_path)

        del wp

    crawl = run
