# -*- coding: utf-8 -*-

"""
pywebcopy.parsers
~~~~~~~~~~~~~~~~~

Custom HTML parsers used in pywebcopy.

Most of the source code is from the MIT Licensed library called
`requests-html` courtesy of kenneth, code has been modified to
fit the needs of this project but some apis are still untouched.



"""


import sys

import bs4
import lxml
from lxml.html.clean import Cleaner
from parse import findall
from parse import search as parse_search
from pyquery import PyQuery
from w3lib.encoding import html_to_unicode

from . import LOGGER, SESSION


PY3 = (sys.version_info[0] == 3)


# HTML style and script tags cleaner
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
            self._lxml = lxml.html.fromstring(self.html)
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
        try:
            converted = bs4.UnicodeDammit(html_string)
            if not converted.unicode_markup:
                raise UnicodeDecodeError("Failed to detect encoding, tried [%s]", ','.join(converted.tried_encodings))
            self.encoding = converted.original_encoding
            return converted.unicode_markup
        except UnicodeDecodeError:
            LOGGER.error("Unicode decoder failed to decode html! Trying fallback..")
            return html_string.decode(self.encoding)

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


class Element(BaseParser, object):
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
