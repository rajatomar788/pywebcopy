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

from . import LOGGER, parsers
from .webpage import WebPage
from .elements import TagBase, LinkTag, ScriptTag, ImgTag
from .exceptions import PywebcopyError

ALL = set()


class UrlAlreadyDownloaded(PywebcopyError):
    """The webpage is already downloaded."""


class AnchorTagHandler(TagBase):
    """Custom anchor tag handler.
    This creates a WebPage objects directly and can start it.
    Replaces the generated webpage objects tranformer by itself
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
        if self.url in ALL:
            LOGGER.debug("Webpage at url %s already downloaded!" % self.url)
            return

        ALL.add(self.url)

        _subpage = self.parser()

        #: overriding the properties of webpage object with the
        #: properties from this transformer object
        _subpage._url_obj = self
        _subpage.url = self.url
        _subpage.get(self.url)
        _subpage.__parse__()
        _subpage.save_complete()

        del _subpage


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

    def __init__(self, base_page_url, webpage_parser_class=None, **kwargs):
        if 'scan_level' in kwargs:
            warnings.warn("The scan_level setting has been deprecated and"
                          "is now not supported. Thus leave it as is.")

        if webpage_parser_class is None:
            self.webpage_parser = WebPage
        else:
            if not isinstance(webpage_parser_class, WebPage):
                TypeError("You need to pass the class, not a instance of it.")
            if not issubclass(webpage_parser_class, WebPage):
                TypeError("Webpage_parser is not of valid type!")

            self.webpage_parser = webpage_parser_class

        self.url = base_page_url

    def run(self):
        """Starts the chain reaction."""

        # parser = self.webpage_parser

        # class Wrapper(AnchorTagHandler):
        #    def __init__(self, *args, **kwargs):
        #        super(Wrapper, self).__init__(*args, parser=parser, **kwargs)

        wrapper = _with_parser(AnchorTagHandler, self.webpage_parser)

        # Recreate the element map
        parsers.element_map = {
            'link'  : LinkTag,
            'style' : LinkTag,
            'script': ScriptTag,
            'img'   : ImgTag,

            'a'     : wrapper,
            'form'  : wrapper,
        }

        #: Prepare a fresh webpage object
        wp = self.webpage_parser()

        #: Fill the data and start
        wp.get(self.url)
        wp.save_complete()

        self.file_path = wp.utx.file_path

        del wp

    crawl = run
