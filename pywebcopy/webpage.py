# encoding: utf-8
"""
pywebcopy.webpage
~~~~~~~~~~~~~~~~~

Python form of a webpage.

Usage::

    >>> from pywebcopy import Webpage, config
    >>> url = 'http://some-url.com/some-page.html'

    # You should always start with setting up the config or use apis
    >>> config.setup_config(url, project_folder, project_name, **kwargs)

    # Create a instance of the webpage object
    >>> wp = Webpage()

    # If you want to use `requests` to fetch the page then
    >>> wp.get(url)

    # Else if you want to use plain html or urllib then use
    >>> wp.set_source(object_which_have_a_read_method, encoding=encoding)
    >>> wp.url = url   # you need to do this if you are using set_source()

    # Then you can access several methods like
    >>> wp.save_complete()
    >>> wp.save_html()
    >>> wp.save_assets()

"""

import logging
import os
import threading
from operator import attrgetter

from .configs import SESSION, config
from .elements import _ElementFactory, LinkTag, ScriptTag, ImgTag, AnchorTag, TagBase
from .exceptions import ParseError
from .parsers import Parser
from .urls import URLTransformer

LOGGER = logging.getLogger('webpage')


class WebPage(Parser, _ElementFactory):
    """Provides the apis for invoking parse and save functionality.

    usage::

        >>> from pywebcopy import WebPage, config
        >>> url = 'http://some-url.com/some-page.html'

        # You should always start with setting up the config or use apis
        >>> config.setup_config(url, project_folder, project_name, **kwargs)

        # Create a instance of the WebPage object
        >>> wp = WebPage()

        # If you want to use `requests` to fetch the page then
        >>> wp.get(url)

        # Else if you want to use plain html or urllib then use
        >>> wp.set_source(object_which_have_a_read_method, encoding=encoding)
        >>> wp.url = url   # you need to do this if you are using set_source()

        # Then you can access several methods like
        >>> wp.save_complete()
        >>> wp.save_html()
        >>> wp.save_assets()

    """

    __slots__ = 'url', '_url_obj', '_element_map', '_stack', 'root', '_tree', \
                'encoding', '_source', '_parseComplete', '_parseBroken'

    def __init__(self, **kwargs):
        super(WebPage, self).__init__()

        if not config.is_set():
            import warnings
            warnings.warn(
                UserWarning(
                    "Global Configuration is not setup. You can ignore this if you are going manual."
                    "This is just one time warning regarding some unexpected behavior."
                )
            )

        # Some scripts might have apis specific to previous version
        # which this doesn't support now and would definitely remove
        # the arguments in later version
        if kwargs.pop('url', None):
            raise DeprecationWarning(
                "Direct initialisation with url is not supported now. Please use"
                "the get() or set_source() methods for page fetching."
                "And use the config.setup_config() method to setup the kwargs."
                "Arguments will be completely removed in later versions."
            )

        self.url = config.get('project_url', None)
        self.path = config.get('project_folder', None)
        self._url_obj = None
        self._element_map = {
            'link': LinkTag,
            'style': LinkTag,
            'script': ScriptTag,
            'img': ImgTag,
            'a': AnchorTag,
            'form': AnchorTag,
            'default': TagBase,
        }
        self._threads = []

    def __repr__(self):
        return '<WebPage: [%s]>' % self.url

    # @property
    # def url(self):
    #     return self.utx.url
    #
    # @url.setter
    # def url(self, new_url):
    #     self.utx.url = new_url

    @property
    def utx(self):
        """Returns an URLTransformer() object made from the self.url string.

        :rtype: URLTransformer
        :returns: prepared URLTransformer object
        """
        if self._url_obj is None:
            self._url_obj = self._new_utx()
        return self._url_obj

    @utx.setter
    def utx(self, o):
        assert isinstance(o, URLTransformer), TypeError
        assert hasattr(o, 'url'), AttributeError
        self._url_obj = o
        self.url = getattr(o, 'url')
        self.path = getattr(o, 'to_path')

    file_path = property(attrgetter('utx.file_path'), doc="Path at which this object would be written.")
    project_path = property(attrgetter('utx.base_path'), doc="Path at which this object would be written.")
    file_name = property(attrgetter('utx.file_name'), doc="Name to be used as the file node.")
    element_map = property(attrgetter('_element_map'), doc="Registry of different handler for different tags.")

    def _get_utx(self):
        return self.utx

    def _new_utx(self):
        assert self.url is not None, "Url not setup."
        assert self.path is not None, "Folder path not setup."

        o = URLTransformer(
            url=self.url,
            base_url=self.url,
            base_path=self.path,
            default_fn='index.html'
        )
        o.default_suffix = 'html'
        o.enforce_suffix = True
        return o

    def _make_element(self, tag):
        # print(self._element_map)
        elem = self._element_map.get(tag)
        if not elem:
            elem = self._element_map.get('default')
        LOGGER.debug('Element: <%r> selected for the tag: <%r>' % (elem, tag))
        return elem

    def get(self, url, **params):
        """Fetches the Html content from Internet using the requests.
        You can any requests params which will be passed to the library
        itself.
        The requests arguments you supply will also be applied to the
        global session meaning all the files will be downloaded using these
        settings.

        If you want to use some manual page fetch, like using urllib, then
        you should use the set_source() method which would do the right job.

        usage::

            >>> wp = WebPage()
            >>> wp.get(url, proxies=proxies, headers=headers, auth=auth, ...)
            >>> wp.save_complete()

        :param url: url of the page to fetch
        :param params: keyword arguments which `requests` module may accept.
        """
        req = SESSION.get(url, **params)
        req.raise_for_status()
        # Set some information about the content being loaded so
        # that the parser has a better idea about
        self.url = req.url
        # The internal parser assumes a read() method to be
        # present on the source, thus we need to pass the raw stream
        # io object which serves the purpose
        req.raw.decode_content = True
        self.set_source(req.raw, req.encoding)

    def save_assets(self):
        """Save only the linked files to the disk.
        """
        if not self.elements:
            LOGGER.error("No elements found for downloading!")
            return

        LOGGER.info("Starting save_assets Action on url: {!r}".format(self.utx.url))

        elms = list(self.elements)

        LOGGER.log(100, "Queueing download of <%d> asset files." % len(elms))

        for elem in elms:
            t = threading.Thread(name=repr(elem), target=elem.run)
            t.start()
            self._threads.append(t)
            # elem.run()

    def save_html(self, file_name=None, raw_html=False):
        """Saves the html of the page to a default or specified file.
        :type file_name: str
        :type raw_html: bool
        :param file_name: path of the file to write the contents to
        :param raw_html: whether write the unmodified html or the rewritten html
        """

        LOGGER.info("Starting save_html Action on url: {!r}".format(self.utx.url))

        if not file_name:
            file_name = self.utx.file_path

        # Create directories if necessary
        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))

        if raw_html:
            src = getattr(self, '_source')
            if not src or not hasattr(src, 'read'):
                raise Exception(
                    "Parser source is not set yet!"
                    "Try .get() method or .set_source() method to feed the parser!"
                )
            with open(file_name, 'wb') as fh:
                fh.write(self.get_source().read())
        else:
            if not getattr(self, '_parseComplete'):
                self.parse()
            root = self.root
            if not hasattr(root, 'getroottree'):
                raise ParseError("Tree is not being generated by parser!")

            root.getroottree().write(file_name, method="html")
            LOGGER.info("WebPage saved successfully to %s" % file_name)

    def save_complete(self):
        """Saves the complete html+assets on page to a file and
        also writes its linked files to the disk.

        Implements the combined logic of save_assets and save_html in
        compact form with checks and validation.
        """

        assert self.url is not None, "Url is not setup."
        assert getattr(self, '_source') is not None, "Source is not setup."

        LOGGER.info("Starting save_complete Action on url: [%r]" % self.url)

        if not self._parseComplete:
            self.parse()  # call in the action

        self.save_assets()
        self.save_html(self.utx.file_path, raw_html=False)
