# Copyright 2020; Raja Tomar
# See license for more details
import logging
import os
import re
import warnings
from base64 import b64encode
from datetime import datetime
from functools import partial
from io import BytesIO
from textwrap import dedent

from lxml.html import HtmlComment
from lxml.html import tostring
from lxml.html import HTMLParser
from lxml.html import XHTML_NAMESPACE
from lxml.html import parse
from requests.models import Response
from six import binary_type
from six import string_types
from six.moves.urllib.request import pathname2url

from .__version__ import __version__
from .helpers import RewindableResponse
from .helpers import cached_property
from .parsers import iterparse
from .parsers import unquote_match
from .urls import get_content_type_from_headers
from .urls import relate
from .urls import retrieve_resource

logger = logging.getLogger(__name__)


class ResponseWrapper(object):
    session = None
    config = None
    context = None
    response = None

    def __del__(self):
        self.close()

    def close(self):
        """Releases the underlying urllib connection and
        then deletes the response"""
        if self.response is not None:
            if hasattr(self.response, 'raw'):
                if hasattr(self.response.raw, 'release_conn'):
                    getattr(self.response, 'raw').release_conn()
            del self.response

    @cached_property
    def content_type(self):
        """Returns a mimetype descriptor of this resource if available."""
        if self.response is not None and 'Content-Type' in self.response.headers:
            return get_content_type_from_headers(self.response.headers)
        return ''

    @cached_property
    def content_encoding(self):
        """Returns an encoding (usually a compression algorithm) of this resource if available."""
        if self.response is not None and 'Content-Encoding' in self.response.headers:
            return self.response.headers['Content-Encoding']
        return ''

    @cached_property
    def url(self):
        """Returns the actual url of this resource which is resolved if
        there were any redirects."""
        if self.response is not None:
            self.context = self.context.with_values(url=self.response.url)
        return self.context.url

    @cached_property
    def encoding(self):
        """Returns an explicit encoding if defined in the config else
        the encoding reported by the server."""
        if self.response is not None:
            #: Explicit encoding takes precedence
            return self.config.get(
                'encoding', self.response.encoding or 'ascii')
        return self.config.get('encoding', 'ascii')

    html_content_types = tuple([
        'text/htm',
        'text/html',
        'text/xhtml'
    ])
    # html_content_types.__doc__ = "Set of valid html mimetypes."

    def viewing_html(self):
        """Checks whether the current resource is a html type or not."""
        return self.content_type in self.html_content_types

    css_content_types = tuple([
        'text/css',
    ])
    # css_content_types.__doc__ = "Set of valid css mimetypes."

    def viewing_css(self):
        """Checks whether the current resource is a css type or not."""
        return self.content_type in self.css_content_types

    js_content_types = tuple([
        'text/javascript',
        'application/javascript'
    ])
    # js_content_types.__doc__ = "Set of valid javascript mimetypes."

    def viewing_js(self):
        """Checks whether the current resource is a javascript type or not."""
        return self.content_type in self.js_content_types

    svg_content_types = tuple([
        'image/svg+xml'
    ])

    def viewing_svg(self):
        """Checks whether the current resource is a svg type or not."""
        return self.content_type in self.svg_content_types

    def set_response(self, response):
        """Update the response attribute of this object.

        It also updates the content_type and encoding as reported by the
        server implicitly for better detection of contents."""
        self.response = response

        #: Clear the cached properties
        self.__dict__.pop('url', None)
        self.__dict__.pop('filepath', None)
        self.__dict__.pop('filename', None)
        if hasattr(response, 'ok') and response.ok:
            self.__dict__.pop('content_type', None)
            self.__dict__.pop('encoding', None)
            self.context = self.context.with_values(
                url=response.url,
                content_type=self.content_type)

    def request(self, method, url, **params):
        """Fetches the Html content from Internet using the requests.
        You can any requests params which will be passed to the library
        itself.
        The requests arguments you supply will also be applied to the
        global session meaning all the files will be downloaded using these
        settings.

        :param method: http verb for transport.
        :param url: url of the page to fetch
        :param params: keyword arguments which `requests` module may accept.
        """
        if params.pop('stream', None):
            warnings.warn(UserWarning(
                "Stream attribute is True by default for reasons."
            ))
        self.set_response(
            self.session.request(method, url, stream=True, **params))

    def get(self, url, **params):
        """Initiates an `get` request for the given url.
        It uses the `.set_response()` method underneath to
        process the returned response.
        It is used to manually fetch the starting web-page.

        Example:
            wp = WebPage()
            wp.get('https://www.example.com/')
            wp.retrieve()
        """
        return self.request('GET', url, **params)

    def post(self, url, **params):
        """Initiates an `post` request for the given url.
        It uses the `.set_response()` method underneath to
        process the returned response.
        It is required to submit forms.

        Example:
            wp = WebPage()
            wp.post('https://www.example.com/', data={'key': 'value'})
            wp.retrieve()
        """
        return self.request('POST', url, **params)

    def get_source(self, buffered=False):
        """
        Returns a tuple with the response contents in either file-like object
        i.e. `RewindableResponse` if `buffered=True` or string format
        if ` buffered=False` and the encoding from the `.encoding` attribute.

        Example:
            wp.get(url=...)
            wp.get_source(buffered=False)
            "<html><head></head><body>...</body></html>"
            wp.get_source(buffered=True)
            "<RewindableResponse(url=...)>"

        Note:
            An Error would be raised if the `.context` attribute is not set.
            or the `.response` attribute is not set.

        :rtype: string_types | RewindableResponse
        """
        if self.context is None:
            raise ValueError("Context not set.")
        if self.context.base_path is None:
            raise ValueError("Context Base Path is not set!")
        if self.context.base_url is None:
            raise ValueError("Context Base url is not Set!")
        if self.response is None:
            raise ValueError("Response attribute is not Set!")
        if getattr(self.response.raw, 'closed', True):
            raise ValueError(
                "I/O operations closed on the response object.")
        if not hasattr(self.response.raw, 'read'):
            raise ValueError(
                "Response must have a raw file like object!")

        self.response.raw.decode_content = True
        if buffered:
            return self.response.raw, self.encoding
        return self.response.content, self.encoding



class GenericResource(ResponseWrapper):
    def __init__(self, session, config, scheduler, context, response=None):
        """
        Generic internet resource which processes a server response based on responses
        content-type. Downloadable file if allowed in config would be downloaded. Css
        file would be parsed using a suitable parser. Html will also be parsed using
        suitable html parser.

        :param session: http client used for networking.
        :param config: project configuration handler.
        :param response: http response from the server.
        :param scheduler: response processor scheduler.
        :param context: context of this response; should contain base-location, base-url etc.
        """
        self.session = session
        self.config = config
        self.scheduler = scheduler
        self.context = context
        self.response = None
        if response:
            self.set_response(response)
        self.logger = logger.getChild(self.__class__.__name__)

    def __repr__(self):
        return '<%s(url=%s)>' % (self.__class__.__name__, self.context.url)

    @cached_property
    def filepath(self):
        """Returns if available a valid filepath
         where this file should be written."""
        if self.context is None:
            raise AttributeError("Context attribute is not set.")
        if self.response is not None:
            ctypes = get_content_type_from_headers(self.response.headers)
            self.context = self.context.with_values(content_type=ctypes)
        return self.context.resolve()

    @cached_property
    def filename(self):
        """Returns a valid filename of this resource if available."""
        return os.path.basename(self.filepath or '')

    def retrieve(self):
        """Retrieves the readable resource to the local disk."""
        if self.response is None:
            raise AttributeError(
                "Response attribute is not set!"
                "You need to fetch the resource using get method!"
            )
        # XXX: Validate resource here?
        return self._retrieve()

    def _retrieve(self):
        #: Not ok response received from the server
        if not 100 <= self.response.status_code <= 400:
            self.logger.error(
                'Status Code [<%d>] received from the server [%s]'
                % (self.response.status_code, self.response.url)
            )
            if isinstance(self.response.reason, binary_type):
                content = BytesIO(self.response.reason)
            else:
                content = BytesIO(self.response.reason.encode(self.encoding))
        else:
            if not hasattr(self.response, 'raw'):
                self.logger.error(
                    "Response object for url <%s> has no attribute 'raw'!"
                    % self.url)
                content = BytesIO(self.response.content)
            elif self.viewing_svg() and self.content_encoding == 'gzip':
                content = BytesIO(self.response.content)
            else:
                content = self.response.raw

        retrieve_resource(
            content, self.filepath, self.context.url, self.config.get('overwrite'))
        del content
        return self.filepath

    def resolve(self, parent_path=None):
        """Returns a relative url at which this resource should be accessed
        by the parent file.
        """
        filepath = self.filepath
        if not isinstance(filepath, string_types):
            raise ValueError("Invalid filepath [%r]" % filepath)
        if parent_path and isinstance(parent_path, string_types):
            return pathname2url(relate(filepath, parent_path))
        return pathname2url(filepath)


class HTMLResource(GenericResource):
    """Interpreter for resource written in or reported as html."""

    def parse(self, **kwargs):
        """Returns an `pywebcopy.parsers.iterparse` instance with
        the file-object returned from the `.get_source(buffered=True)`.

        :params kwargs: options to be passed to the `iterparse`.
        """
        source, encoding = self.get_source(buffered=True)
        return iterparse(
            source, encoding, include_meta_charset_tag=True, **kwargs)

    def extract_children(self, parsing_buffer):
        """
        Iterates over the `pywebcopy.parsers.iterparse` object and
        extract the elements which are handed over to the `scheduler`
        for processing. Then the final path of the element is updated
        in the `pywebcopy.parsers.iterparse` object.

        :param parsing_buffer: `iterparse` object.
        """
        location = self.filepath

        for elem, attr, url, pos in parsing_buffer:
            if not self.scheduler.validate_url(url):
                continue

            sub_context = self.context.create_new_from_url(url)
            ans = self.scheduler.get_handler(
                elem.tag,
                self.session, self.config, self.scheduler, sub_context)
            self.scheduler.handle_resource(ans)
            resolved = ans.resolve(location)
            elem.replace_url(url, resolved, attr, pos)

        return parsing_buffer

    def _retrieve(self):
        if not self.viewing_html():
            self.logger.info(
                "Resource of type [%s] is not HTML." % self.content_type)
            return super(HTMLResource, self)._retrieve()

        if not self.response.ok:
            self.logger.debug(
                "Resource at [%s] is NOT ok and will be NOT processed." % self.url)
            return super(HTMLResource, self)._retrieve()

        context = self.extract_children(self.parse())

        # WaterMarking :)
        context.root.insert(0, HtmlComment(self._get_watermark()))

        retrieve_resource(
            BytesIO(tostring(context.root, include_meta_content_type=True)),
            self.filepath, self.context.url, overwrite=True)

        self.logger.debug('Retrieved content from the url: [%s]' % self.url)
        del context
        return self.filepath

    def _get_watermark(self):
        # comment text should be in Unicode
        return dedent("""
        * PyWebCopy Engine [version %s]
        * Copyright 2020; Raja Tomar
        * File mirrored from [%s]
        * At UTC datetime: [%s]
        """) % (__version__, self.response.url, datetime.utcnow())


class WebElement(HTMLResource):
    """
    WebPage built upon HTMLResource element.
    It provides various utilities like form-filling,
    external response processing, getting list of links,
    dumping html and opening the html in the browser.
    """

    def __repr__(self):
        """Short representation of this instance."""
        return '<{}: {}>'.format(self.__class__.__name__, self.url)

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
        return super(WebElement, self).set_response(response)

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
        if not self.viewing_html():
            raise TypeError(
                "Not viewing a html page. Please check the link!")

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


class CSSResource(GenericResource):
    def parse(self):
        """Returns the `.get_source(buffered=False)`."""
        return self.get_source(buffered=False)

    def repl(self, match, encoding=None, fmt=None):
        """
        Schedules the linked files for downloading then resolves their references.
        """
        fmt = fmt or '%s'

        url, _ = unquote_match(match.group(1).decode(encoding), match.start(1))
        self.logger.debug("Sub-Css resource found: [%s]" % url)

        if not self.scheduler.validate_url(url):
            return url.encode(encoding)

        sub_context = self.context.create_new_from_url(url)
        self.logger.debug('Creating context for url: %s as %s' % (url, sub_context))
        ans = self.__class__(
            self.session, self.config, self.scheduler, sub_context
        )
        # self.children.add(ans)
        self.logger.debug("Submitting resource: [%s] to the scheduler." % url)
        self.scheduler.handle_resource(ans)
        re_enc = (fmt % ans.resolve(self.filepath)).encode(encoding)
        self.logger.debug("Re-encoded the resource: [%s] as [%r]" % (url, re_enc))
        return re_enc

    # noinspection PyTypeChecker
    def extract_children(self, parsing_buffer):
        """
        Runs the regex over the source to find the urls that are linked
        within the css file or style tag using the `url()` construct.
        """
        source, encoding = parsing_buffer
        source = re.sub(
            (r'url\((' + '["][^"]*["]|' + "['][^']*[']|" + r'[^)]*)\)').encode(encoding),
            partial(self.repl, encoding=encoding, fmt="url('%s')"),
            source, flags=re.IGNORECASE
        )
        source = re.sub(
            r'@import "(.*?)"'.encode(encoding),
            partial(self.repl, encoding=encoding, fmt='"%s"'),
            source, flags=re.IGNORECASE
        )
        return BytesIO(source)

    def _retrieve(self):
        """Writes the modified buffer to the disk."""
        if not self.viewing_css():
            self.logger.info(
                "Resource of type [%s] is not CSS." % self.content_type)
            return super(CSSResource, self)._retrieve()

        if not self.response.ok:
            self.logger.debug(
                "Resource at [%s] is NOT ok and will be NOT processed." % self.url)
            return super(CSSResource, self)._retrieve()

        self.logger.debug(
            "Resource at [%s] is ok and will be processed." % self.url)
        retrieve_resource(
            self.extract_children(self.parse()),
            self.filepath, self.url, self.config.get('overwrite')
        )
        self.logger.debug("Finished processing resource [%s]" % self.url)
        return self.filepath


class JSResource(GenericResource):
    def parse(self):
        """Returns the `.get_source(buffered=False)`."""
        return self.get_source(buffered=False)

    def repl(self, match, encoding=None, fmt=None):
        """
        Schedules the linked files for downloading then resolves their references.
        """
        fmt = fmt or '%s'

        url, _ = unquote_match(match.group(1).decode(encoding), match.start(1))
        self.logger.debug("Sub-JS resource found: [%s]" % url)

        if not self.scheduler.validate_url(url):
            return url.encode(encoding)

        sub_context = self.context.create_new_from_url(url)
        self.logger.debug('Creating context for url: %s as %s' % (url, sub_context))
        ans = self.__class__(
            self.session, self.config, self.scheduler, sub_context
        )
        # self.children.add(ans)
        self.logger.debug("Submitting resource: [%s] to the scheduler." % url)
        self.scheduler.handle_resource(ans)
        re_enc = (fmt % ans.resolve(self.filepath)).encode(encoding)
        self.logger.debug("Re-encoded the resource: [%s] as [%r]" % (url, re_enc))
        return re_enc

    # noinspection PyTypeChecker
    def extract_children(self, parsing_buffer):
        """
        Runs the regex over the source to find the urls that are linked
        within the js file or script tag using the `url()` construct.

        ..todo::
            It only recognises one type of url inside of the js.
            i.e. `url('example.com')`. Make it universal.
        """
        source, encoding = parsing_buffer
        # P.S. There is one interesting Regex on this github repo under MIT license
        # https://github.com/GerbenJavado/LinkFinder/
        source = re.sub(
            (r'url\((' + '["][^"]*["]|' + "['][^']*[']|" + r'[^)]*)\)'
             ).encode(encoding),
            partial(
                self.repl, encoding=encoding, fmt='url("%s")'
            ), source, flags=re.IGNORECASE
        )
        return BytesIO(source)

    def _retrieve(self):
        """Writes the modified buffer to the disk."""
        if not self.viewing_js():
            self.logger.info("Resource of type [%s] is not JS." % self.content_type)
            return super(JSResource, self)._retrieve()

        if not self.response.ok:
            self.logger.debug("Resource at [%s] is NOT ok and will be NOT processed." % self.url)
            return super(JSResource, self)._retrieve()

        self.logger.debug("Resource at [%s] is ok and will be processed." % self.url)
        retrieve_resource(
            self.extract_children(self.parse()),
            self.filepath, self.url, self.config.get('overwrite')
        )
        self.logger.debug("Finished processing resource [%s]" % self.url)
        return self.filepath


class GenericOnlyResource(GenericResource):
    """Only retrieves a resource if it is NOT HTML."""

    def _retrieve(self):
        if self.viewing_html():
            self.logger.debug("Resource [%s] is of HTML type and must not be processed!" % self.url)
            return False
        return super(GenericOnlyResource, self)._retrieve()

    def resolve(self, parent_path=None):
        if self.viewing_html():
            return self.context.url
        return super(GenericOnlyResource, self).resolve(parent_path=parent_path)


class VoidResource(GenericResource):
    def get(self, url, **params):
        return None

    def get_source(self, buffered=False):
        return None

    def retrieve(self):
        return None


# :)
NullResource = VoidResource


class UrlRemover(VoidResource):
    def resolve(self, parent_path=None):
        return '#'


class AbsoluteUrlResource(VoidResource):
    def resolve(self, parent_path=None):
        return self.context.url


class Base64Resource(GenericResource):
    def resolve(self, parent_path=None):
        source, encoding = self.get_source()
        import sys
        if sys.version > '3':
            if type(source) is bytes:
                return 'data:%s;base64,%s' % (self.content_type, bytes.decode(b64encode(source)))
            else:
                return 'data:%s;base64,%s' % (self.content_type, bytes.decode(b64encode(str.encode(source, encoding))))
        else:
            return 'data:%s;base64,%s' % (self.content_type, b64encode(source))

    def retrieve(self):
        #: There are no sub-files to be fetched.
        return None
