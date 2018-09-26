# -*- coding: utf-8 -*-

"""
pywebcopy.parsers
~~~~~~~~~~~~~~~~~

Custom HTML parsers used in pywebcopy.

"""

import os
import io
import re
import sys
import requests
import bs4
import lxml
from bs4 import UnicodeDammit
from lxml import html, etree
from lxml.html import tostring
from lxml.html.clean import Cleaner
from parse import findall
from parse import search as parse_search
from pyquery import PyQuery
from w3lib.encoding import html_to_unicode

from pywebcopy import LOGGER, SESSION
from pywebcopy.config import config
from pywebcopy.core import new_file
from pywebcopy.elements import Asset
from pywebcopy.elements import LinkTag, AnchorTag
from pywebcopy.elements import FileMixin
from pywebcopy.elements import ImgTag
from pywebcopy.elements import ScriptTag
from pywebcopy.exceptions import InvalidUrlError
from pywebcopy.urls import Url
from pywebcopy.utils import relate

try:
    from urllib import pathname2url
    from urlparse import urljoin
except ImportError:
    # noinspection PyCompatibility
    from urllib.parse import urljoin
    from urllib.request import pathname2url

PY3 = (sys.version_info[0] == 3)
CSS_URLS = re.compile(b'''url\\(['|"]?(.*?)["|']?\\)''')
ENCODING = re.compile(r'charset=([\w_-]+)')

# HTML cleaner
cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True


class BaseParser:
    """Parses the webpage and makes several internal and external available.

    :param element: PyQuery object or raw html
    :param url: url of the webpage or site
    :param default_encoding: optional explicit declaration of encoding type of that webpage
    :param HTML: plain html markup string
    """

    def __init__(self, element=None, url=None, default_encoding=None, HTML=None):
        # type: (object or str, str, str, str or object) -> object
        self.element = element
        self.url = url
        self._useDefaultDecoder = False
        self.default_encoding = default_encoding
        self._encoding = None
        self._html = HTML
        self._lxml = None
        self._pq = None
        self._soup = None
        self._request = None
        self._isParsed = False
        self._prepped = False
        self._readContent = b''

    @property
    def lxml(self):
        """Parses the decoded self.html contents after decoding it by itself
        decoding detector (default) or decoding it using provided self.default_encoding.
        """

        if self._lxml is None:
            self._lxml = html.fromstring(self.html)
        return self._lxml

    @property
    def bs4(self):
        """BeautifulSoup object under the hood.
        Read more about beautifulsoup at https://www.crummy.com/software/BeautifulSoup/doc
        """

        if self._soup is None:
            self._soup = bs4.BeautifulSoup(self.raw_html, 'html.parser')
        return self._soup

    @property
    def raw_html(self):
        """Bytes representation of the HTML content.
        (`learn more <http://www.diveintopython3.net/strings.html>`_).
        """
        if self._html:
            return self._html
        else:
            return lxml.html.tostring(self.element, encoding=self.encoding)

    @raw_html.setter
    def raw_html(self, HTML):
        """Property setter for self.html."""
        self._html = HTML

    @property
    def html(self):
        """Unicode representation of the HTML content."""
        if self._html:
            if not self._useDefaultDecoder:
                LOGGER.info("Using Forced Encoding %r on raw_html!" % self.encoding)
                return self.raw_html.decode(self.encoding, errors='xmlcharrefreplace')
            else:
                LOGGER.info("Using default Codec on raw_html!")
                return self.decode_html(self.raw_html)
        else:
            return lxml.html.tostring(self.element, encoding='unicode').strip()

    @html.setter
    def html(self, HTML):
        """Property setter for self.html"""
        if not isinstance(HTML, str):
            raise TypeError
        self._html = HTML.decode(self.encoding, errors='xmlcharrefreplace')

    def decode_html(self, html_string):
        converted = UnicodeDammit(html_string)
        if not converted.unicode_markup:
            raise UnicodeDecodeError("Failed to detect encoding, tried [%s]", ','.join(converted.tried_encodings))
        self.encoding = converted.original_encoding
        return converted.unicode_markup

    def encode(self, encoding=None, errors='xmlcharrefreplace'):
        """Returns the html of this :class: encoded with specified encoding."""
        return self.html.encode(encoding=encoding, errors=errors)

    @property
    def encoding(self):
        """The encoding string to be used, extracted from the HTML and
        :class:`HTMLResponse <HTMLResponse>` headers.
        """
        if self._encoding:
            return self._encoding

        # Scan meta tags for charset.
        if self._html:
            self._encoding = html_to_unicode(self.default_encoding, self._html)[0]
            # Fall back to requests' detected encoding if decode fails.
            try:
                self.raw_html.decode(self.encoding, errors='replace')
            except UnicodeDecodeError:
                self._encoding = self.default_encoding

        return self._encoding if self._encoding else self.default_encoding

    @encoding.setter
    def encoding(self, enc):
        """Property setter for self.encoding."""
        self._encoding = enc

    @property
    def pq(self):
        """`PyQuery <https://pythonhosted.org/pyquery/>`_ representation
        of the :class:`Element <Element>` or :class:`HTML <HTML>`.
        """
        if self._pq is None:
            self._pq = PyQuery(self.lxml)

        return self._pq

    @property
    def text(self):
        """The text content of the
        :class:`Element <Element>` or :class:`HTML <HTML>`.
        """
        return self.pq.text()

    @property
    def full_text(self):
        """The full text content (including links) of the
        :class:`Element <Element>` or :class:`HTML <HTML>`.
        """
        return self.lxml.text_content()

    def find(self, selector="*", containing=None, clean=False, first=False,
             _encoding=None):
        """Given a CSS Selector, returns a list of
        :class:`Element <Element>` objects or a single one.

        :param selector: CSS Selector to use.
        :param clean: Whether or not to sanitize the found HTML of ``<script>`` and ``<style>`` tags.
        :param containing: If specified, only return elements that contain the provided text.
        :param first: Whether or not to return just the first result.
        :param _encoding: The encoding format.

        Example CSS Selectors:

        - ``a``
        - ``a.someClass``
        - ``a#someID``
        - ``a[target=_blank]``

        See W3School's `CSS Selectors Reference
        <https://www.w3schools.com/cssref/css_selectors.asp>`_
        for more details.

        If ``first`` is ``True``, only returns the first
        :class:`Element <Element>` found.
        """

        # Convert a single containing into a list.
        if isinstance(containing, str):
            containing = [containing]
        if not isinstance(selector, str):
            raise TypeError("Expected string, got %r" % type(selector))

        encoding = _encoding or self.encoding
        elements = [
            Element(element=found, url=self.url, default_encoding=encoding)
            for found in self.pq(selector)
        ]

        if containing:
            elements_copy = list(elements)
            elements = []

            for element in elements_copy:
                if any([c.lower() in element.full_text.lower() for c in containing]):
                    elements.append(element)

            elements.reverse()

        # Sanitize the found HTML.
        if clean:
            elements_copy = list(elements)
            elements = []

            for element in elements_copy:
                element.raw_html = lxml.html.tostring(cleaner.clean_html(element.lxml))
                elements.append(element)

        if first and len(elements) > 0:
            return elements[0]
        else:
            return elements

    def xpath(self, selector, clean=False, first=False, _encoding=None):
        """Given an XPath selector, returns a list of
        :class:`Element <Element>` objects or a single one.

        :param selector: XPath Selector to use.
        :param clean: Whether or not to sanitize the found HTML of ``<script>`` and ``<style>`` tags.
        :param first: Whether or not to return just the first result.
        :param _encoding: The encoding format.

        If a sub-selector is specified (e.g. ``//a/@href``), a simple
        list of results is returned.

        See W3School's `XPath Examples
        <https://www.w3schools.com/xml/xpath_examples.asp>`_
        for more details.

        If ``first`` is ``True``, only returns the first
        :class:`Element <Element>` found.
        """
        if not isinstance(selector, str):
            raise TypeError("Expected string, got %r" % type(selector))

        selected = self.lxml.xpath(selector)

        elements = [
            Element(element=selection, url=self.url, default_encoding=_encoding or self.encoding)
            if not isinstance(selection, lxml.etree._ElementUnicodeResult) else str(selection)
            for selection in selected
        ]

        # Sanitize the found HTML.
        if clean:
            elements_copy = list(elements)
            elements = []

            for element in elements_copy:
                element.raw_html = lxml.html.tostring(cleaner.clean_html(element.lxml))
                elements.append(element)

        if first and len(elements) > 0:
            return elements[0]
        else:
            return elements

    def search(self, template):
        """Search the :class:`Element <Element>` for the given Parse template.

        :param template: The Parse template to use.
        """
        if not isinstance(template, str):
            raise TypeError("Expected string, got %r" % type(template))

        return parse_search(template, self.html)

    def search_all(self, template):
        """Search the :class:`Element <Element>` (multiple times) for the given parse
        template.

        :param template: The Parse template to use.
        """
        if not isinstance(template, str):
            raise TypeError("Expected string, got %r" % type(template))

        return [r for r in findall(template, self.html)]


class UrlHandler:
    """Handles different url types in the webpage."""

    def __init__(self, base_url=None, base_path=None):
        self.base_url = base_url
        self.base_path = base_path
        self._store = []
        self._urlMap = {}

        LOGGER.info("Url Handler initiated with base_url: %s and base_path: %s" % (base_url, base_path))

    @property
    def elements(self):
        return self._store

    def _base_handler(self, elem, attr, url, pos):
        """Can handle <img>, <link>, <script> :class: `lxml.html.Element` object."""
        LOGGER.debug("Handling url %s" % url)

        if url.startswith(u"#") or url.startswith(u"data:") or url.startswith(u'javascript'):
            return None  # not valid link

        try:
            if elem.tag == 'link':
                obj = LinkTag(url)
            elif elem.tag == 'script':
                obj = ScriptTag(url)
            elif elem.tag == 'img':
                obj = ImgTag(url)
            elif elem.tag == 'a':
                obj = AnchorTag(url)
            else:
                obj = Asset(url)

            obj.base_url = self.base_url
            obj.tag = attr
            obj.rel_path = pathname2url(relate(obj.file_path, self.base_path))
            self._store.append(obj)
            return obj

        except Exception as e:
            LOGGER.error(e)
            LOGGER.error('Exception occurred while creating an object for %s' % url)
            return None  # return unmodified

    def default_handler(self, elem, attr, url, pos):
        """Handles any link type <a> <link> <script> <style> <style url>.
        Note: Default handler function structures makes use of .rel_path attribute
        which is completely internal and any usage depending on this attribute
        may not work properly.
        """
        obj = self._base_handler(elem, attr, url, pos)

        if obj is None:
            return

        if attr is None:
            new = elem.text[:pos] + obj.rel_path + elem.text[len(url) + pos:]
            elem.text = new
        else:
            cur = elem.get(attr)
            if not pos and len(cur) == len(url):
                new = obj.rel_path  # most common case
            else:
                new = cur[:pos] + obj.rel_path + cur[pos + len(url):]

            elem.set(attr, new)
        LOGGER.info("Remapped url of the file: %s to the path: %s " % (url, obj.rel_path))
        self._urlMap[url] = obj.rel_path
        return obj

    def handle(self, elem, attr, url, pos):
        """Base handler function."""
        if url.startswith(u'#') or url.startswith(u'java') or \
                url.startswith(u'data') or not url.strip('/') or not url.strip():
            return url

        if not self.base_url:
            raise AttributeError("Url attributes are unset!")

        _handler = self.default_handler(elem, attr, url, pos)

        if not _handler:
            LOGGER.debug("No handler found for the link of type %s !" % elem.tag)
            return url  # return unmodified
        else:
            return _handler


class WebPage(BaseParser, object):
    """Provides scraping and parsing and saving ability in one class."""

    def __init__(self, url, project_folder=None, project_name=None, encoding=None,
                 force_decoding=False, HTML=None, url_handler=None, **kwargs):
        self.original_url = url
        self._url = url if HTML else None
        self._request = None

        config.setup_config(url, project_folder, project_name, **kwargs)

        if not HTML and (not self.request or not self.request.ok):
            raise InvalidUrlError("Provided url didn't work %s" % url)

        self._url_obj = None
        self._url_handler = url_handler

        super(WebPage, self).__init__(
            element=HTML,
            url=self.url,
            default_encoding=encoding or 'utf-8' if HTML else self.request.encoding,
            HTML=HTML or self.request.content,
        )

        self.force_decoding = force_decoding
        if not self.force_decoding:
            self._useDefaultDecoder = True

    @property
    def url(self):
        """Returns a url as reported by the server."""
        if self._url is None:
            self._url = self.request.url
        return self._url

    @url.setter
    def url(self, new_url):
        self._url = new_url

    @property
    def url_obj(self):
        """Returns an Url() object made from the self.url string.
        :returns: Url() object"""
        if self._url_obj is None:
            self._url_obj = Url(self.url)
            self._url_obj.base_path = config['project_folder']
            self._url_obj.default_filename = 'index.html'
            self._url_obj._unique_fn_required = False
        return self._url_obj

    @property
    def url_handler(self):
        if self._url_handler is None:
            self._url_handler = UrlHandler(self.url, self.url_obj.file_path)
        return self._url_handler

    @property
    def request(self):
        """Makes a http request to the server and sets the .http_request attribute to
        returned response."""

        if not self._request:
            self._request = SESSION.get(self.original_url, stream=True)

            if self._request is None:
                raise InvalidUrlError("Webpage couldn't be loaded from url %s" % self.original_url)

        return self._request

    @request.setter
    def request(self, requestsResponseObject):
        """Sets the base"""

    @property
    def htmlStream(self):
        """Returns a stream of data fetched from the objects url attribute."""
        return io.BytesIO(self.html)

    def linkedElements(self, tags=None):
        """Returns every linked file object as :class: `lxml.html.Element` (multiple times)."""

        for elem in self.url_handler.elements:
            if not tags:
                yield elem
            else:
                if elem.tag in tags:
                    yield elem

    def _extractLinks(self):
        """Rewrites url in document root."""
        # `lxml.html` object has a `.iterlinks` function which is crucial for this
        # task to be completed.
        if self.lxml is None:
            raise RuntimeError("Couldn't generate a etree object for the url %s" % self.url)

        # stores the etree.html object generated by the lxml in the attribute
        for i in self.lxml.iterlinks():
            self.url_handler.handle(*i)

    def _remapImages(self):
        """Rewrites <img> attributes if it have an srcset type attribute which prevents rendering of img
        from its original src attribute url."""

        if self.lxml is None:
            raise RuntimeError("Couldn't rewrite images for the url %s" % self.url)

        set_url = re.compile(r'((?:https?:\/|)[\w\/\.\\_-]+)')

        for elem in self.lxml.xpath('.//img[@*]'):
            _keys = elem.attrib.keys()
            LOGGER.debug("Pre-Attributes for the imgs")
            LOGGER.debug(elem.attrib)
            if 'src' in _keys: # element would be catched later while saving files
                elem.attrib.update({'data-src': '', 'data-srcset': '', 'srcset':''})
            elif 'data-src' in _keys:
                elem.attrib.update({'data-src': '', 'data-srcset': '', 'srcset': '', 'src': elem.attrib['data-src']})
            elif 'data-srcset' in _keys:
                _first_url = set_url.findall(elem.attrib.get('data-srcset'))[0]
                elem.attrib.update({'data-srcset': '', 'data-src': '', 'srcset': '', 'src': _first_url})
            elif 'srcset' in _keys:
                _first_url = set_url.findall(elem.attrib.get('srcset'))[0]
                elem.attrib.update({'data-srcset': '', 'data-src': '', 'srcset': '', 'src': _first_url})
            else:
                pass    # unknown case
            LOGGER.debug("Remapped Attributes of the img.")
            LOGGER.debug(elem.attrib)

    def get(self, url, use_global_session=True, **requestskwargs):
        """Fetches the Html content from Internet.

        :param url: url of the webpage to fetch
        :param use_global_session: if you would like later http requests made to server to follow the
        same configuration as you provided then leave it to 'True' else if you want
        only single http request to follow these configuration set it to 'False'.
        :param **requestskwargs: keyword arguments which `requests` module may accept.
        """
        if use_global_session:
            self.html = SESSION.get(url, **requestskwargs).content
        else:
            self.html = requests.get(url, **requestskwargs).content

    def save_html(self, file_name=None, raw_html=True):
        """Saves the html of the page to a default or specified file.

        :param file_name: path of the file to write the contents to
        :param raw_html: whether write the unmodified html or the rewritten html
        """
        if raw_html:
            with open(file_name or self.url_obj.file_path, 'wb') as fh:
                fh.write(self.raw_html)
        else:
            self.lxml.getroottree().write(file_name or self.url_obj.file_path, method="html")

    def save_assets(self, base_path=None, reset_html=True):
        """Save only the linked files to the disk.

        :param base_path: folder in which to store the files.
        :param reset_html: whether to write modified file locations to the html content
        of this object
        """

        if base_path and not os.path.isdir(base_path):
            raise ValueError("Provided path is not a valid directory! %" % base_path)

        self._remapImages()
        self._extractLinks()
        for elem in self.url_handler.elements:
            try:
                if base_path:
                    elem.base_path = base_path
                elem.save_file()
            except Exception as e:
                LOGGER.error("Linked file generated an error upon saving!")
                LOGGER.error(e)
                pass

        if reset_html:
            self._lxml = None   # reset the ElementTree

    def save_complete(self):
        """Saves the complete html page to a file and also writes its linked files to the disk."""
        self.save_assets(reset_html=False)
        # new_file(self.url_obj.file_path, content=tostring(self.lxml, encoding=self.encoding))
        self.lxml.getroottree().write(self.url_obj.file_path, method="html")

        self._lxml = None # reset the tree


class Element(BaseParser):
    """An element of HTML.

    :param element: The element from which to base the parsing upon.
    :param url: The URL from which the HTML originated, used for ``absolute_links``.
    :param default_encoding: Which encoding to default to.
    """

    def __init__(self, element, url, default_encoding=None):
        super(Element, self).__init__(element=element, url=url, default_encoding=default_encoding)
        self.element = element
        self.tag = element.tag
        self.lineno = element.sourceline
        self._attrs = None

    def __repr__(self):
        attrs = ['{}={}'.format(attr, repr(self.attrs[attr])) for attr in self.attrs]
        return "<Element {} {}>".format(repr(self.element.tag), ' '.join(attrs))

    @property
    def attrs(self):
        """Returns a dictionary of the attributes of the :class:`Element <Element>`
        (`learn more <https://www.w3schools.com/tags/ref_attributes.asp>`_).
        """
        if self._attrs is None:
            self._attrs = {k: v for k, v in self.element.items()}

            # Split class and rel up, as there are usually many of them:
            for attr in ['class', 'rel']:
                if attr in self._attrs:
                    self._attrs[attr] = tuple(self._attrs[attr].split())

        return self._attrs


def parse(url, parser='html5lib', **kwargs):
    """Provides BeautifulSoup objects after custom checks.

    Parser for the bs4 is defaulted to 'html5lib'.

    Example:
    >>> parsed_html = parse('http://some-site.com/')
    """
    return bs4.BeautifulSoup(SESSION.get(url).content, features=parser, **kwargs)


def parse_content(content, parser='html5lib', **kwargs):
    """Returns the parsed content from provided markup."""

    return bs4.BeautifulSoup(content, features=parser, **kwargs)
