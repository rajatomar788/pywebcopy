# Copyright 2020; Raja Tomar
# See license for more details
import logging
import operator
import os

from lxml.html import HTMLParser
from lxml.html import XHTML_NAMESPACE
from lxml.html import parse
from requests.models import Response

from .elements import HTMLResource
from .helpers import RewindableResponse
from .schedulers import crawler_scheduler
from .schedulers import default_scheduler
from .schedulers import threading_crawler_scheduler
from .schedulers import threading_default_scheduler

__all__ = ['WebPage', 'Crawler']

logger = logging.getLogger(__name__)


class WebPage(HTMLResource):
    """
    WebPage built upon HTMLResource element.
    It provides various utilities like form-filling,
    external response processing, getting list of links,
    dumping html and opening the html in the browser.
    """
    @classmethod
    def from_config(cls, config):
        """It creates a `WebPage` object from a set config object.
        Under the hood it checks whether the config is set or not,
        then it creates a `session` using the `config.create_session()` method.
        It then creates a `scheduler` based on whether the threading is enabled or not.
        It also defines a `context` object which stores the path metadata for this structure.
        """
        if config and not config.is_set():
            raise AttributeError("Configuration is not setup.")

        session = config.create_session()
        if config.get('threaded'):
            scheduler = threading_default_scheduler(
                timeout=config.get_thread_join_timeout())
        else:
            scheduler = default_scheduler()
        context = config.create_context()
        ans = cls(session, config, scheduler, context)
        # XXX: Check connection to the url here?
        return ans

    def __repr__(self):
        """Short representation of this instance."""
        return '<{}: {}>'.format(self.__class__.__name__, self.url)

    element_map = property(
        operator.attrgetter('scheduler.data'),
        doc="Registry of different handler for different tags."
    )

    def set_response(self, response):
        """
        Set an explicit `requests.Response` object directly.
        It accepts a `requests.Response` object and wraps it in a `RewindableResponse` object.
        It also enables decoding in the original `urllib3` response object.

        You can use it like this
            import requests
            resp = requests.get('https://www.httpbin.org/')
            wp = WebPage()
            wp.set_response(resp)
            wp.get_forms()
        """
        if not isinstance(response, Response):
            raise ValueError("Expected %r, got %r" % (Response, response))
        response.raw.decode_content = True
        response.raw = RewindableResponse(response.raw)
        return super(WebPage, self).set_response(response)

    def get_source(self, buffered=False):
        """Returns the `requests.Response` object
        in a rewindable io wrapper. Contents can be consumed then
        the `.rewind()` method should be called to restore the contents
        of the original response.

            wp = WebPage()
            wp.get('http://httpbin.org/forms/')
            src = WebPage.get_source(buffered=True)
            contents = src.read()
            src.rewind()

        :param buffered: whether to return an Readable file-like object
            or just a plain string.
        :rtype: RewindableResponse
        """
        raw = getattr(self.response, 'raw', None)
        if raw is None:
            raise ValueError(
                "HTTP Response is not set at the `.response` attribute!"
                "Use the `.get()` method or `.set_response()` methods to set it.")

        # if raw.closed:
        #     raise ValueError(
        #         "I/O operations are closed for the raw source.")

        # Return the raw object which will decode the
        # buffer while reading otherwise errors will follow
        raw.decode_content = True

        # fp = getattr(raw, '_fp', None)
        # assert fp is not None, "Raw source wrapper is missing!"
        # assert isinstance(fp, CallbackFileWrapper), \
        #     "Raw source wrapper is missing!"
        raw.rewind()
        if buffered:
            return raw, self.encoding
        return raw.read(), self.encoding

    def refresh(self):
        """Re-fetches the resource from the internet using the session."""
        self.set_response(self.session.get(self.url, stream=True))

    def get_forms(self):
        """Returns a list of form elements available on the page."""
        source, encoding = self.get_source(buffered=True)
        return parse(
            source, parser=HTMLParser(encoding=encoding, collect_ids=False)
        ).xpath(
            "descendant-or-self::form|descendant-or-self::x:form",
            namespaces={'x': XHTML_NAMESPACE}
        )

    def submit_form(self, form, **extra_values):
        """
        Helper function to submit a `lxml` form.

        Example:

            wp = WebPage()
            wp.get('http://httpbin.org/forms/')
            form = wp.get_forms()[0]
            form.inputs['email'].value = 'bar' # etc
            form.inputs['password'].value = 'baz' # etc
            wp.submit_form(form)
            wp.get_links()

        The action is one of 'GET' or 'POST', the URL is the target URL as a
        string, and the values are a sequence of ``(name, value)`` tuples
        with the form data.
        """
        values = form.form_values()
        if extra_values:
            if hasattr(extra_values, 'items'):
                extra_values = extra_values.items()
            values.extend(extra_values)

        if form.action:
            url = form.action
        elif form.base_url:
            url = form.base_url
        else:
            url = self.url
        return self.request(form.method, url, data=values)

    def get_files(self):
        """
        Returns a list of urls, css, js, images etc.
        """
        return (e[2] for e in self.parse())

    def get_links(self):
        """
        Returns a list of urls in the anchor tags only.
        """
        return (e[2] for e in self.parse() if e[0].tag == 'a')

    def scrap_html(self, url):
        """Returns the html of the given url.

        :param url: address of the target page.
        """
        response = self.session.get(url)
        response.raise_for_status()
        return response.content

    def scrap_links(self, url):
        """Returns all the links from a given url.

        :param url: address of the target page.
        """
        response = self.session.get(url)
        response.raise_for_status()
        return response.links()

    def dump_html(self, filename=None):
        """Saves the html of the page to a default or specified file.

        :param filename: path of the file to write the contents to
        """
        filename = filename or self.filepath
        with open(filename, 'w+b') as fh:
            source, enc = self.get_source()
            fh.write(source)
        return filename

    def save_complete(self, pop=False):
        """Saves the complete html+assets on page to a file and
        also writes its linked files to the disk.

        Implements the combined logic of save_assets and save_html in
        compact form with checks and validation.
        """
        if not self.viewing_html():
            raise TypeError(
                "Not viewing a html page. Please check the link!")

        self.scheduler.handle_resource(self)
        if pop:
            self.open_in_browser()
        return self.filepath

    def open_in_browser(self):
        """Open the page in the default browser if it has been saved.

        You need to use the :meth:`~WebPage.save_complete` to make it work.
        """
        if not os.path.exists(self.filepath):
            self.logger.info(
                "Can't find the file to open in browser: %s" % self.filepath)
            return False

        self.logger.info(
            "Opening default browser with file: %s" % self.filepath)
        import webbrowser
        return webbrowser.open('file:///' + self.filepath)

    # handy shortcuts
    run = crawl = save_assets = save_complete


class Crawler(WebPage):
    @classmethod
    def from_config(cls, config):
        """
        It creates a `Crawler` object from a set config object.
        Under the hood it checks whether the config is set or not,
        then it creates a `session` using the `config.create_session()` method.
        It then creates a `scheduler` based on whether the threading is enabled or not.
        The scheduler is different from the `WebPage` objects scheduler due to its
        ability to process the anchor tags links to different pages.
        It also defines a `context` object which stores the path metadata for this structure.
        """
        if config and not config.is_set():
            raise AttributeError("Configuration is not setup.")

        session = config.create_session()
        if config.get('threaded'):
            scheduler = threading_crawler_scheduler(
                timeout=config.get_thread_join_timeout())
        else:
            scheduler = crawler_scheduler()
        context = config.create_context()
        ans = cls(session, config, scheduler, context)
        # XXX: Check connection to the url here?
        return ans
