# Copyright 2020; Raja Tomar
# See license for more details
import functools
import inspect
import logging
import re

import requests
from lxml import etree
from lxml.html import _nons
from lxml.html import fromstring
from lxml.html import tostring
from lxml.html import XHTML_NAMESPACE
from lxml.html.clean import Cleaner
from lxml.html.defs import link_attrs
from six import next
from six import integer_types
from six import string_types
from six.moves.urllib.parse import urljoin
from six.moves.collections_abc import Iterator

__all__ = ['iterparse', 'MultiParser', 'Element', 'unquote_match', 'links']

logger = logging.getLogger(__name__)

# Attributes which contains multiple links.
srcset_attrs = frozenset([
    'srcset', 'data-srcset', 'src-set', 'imageset',
])
_iter_srcset_urls = re.compile(r"([^\s,]{4,})", re.MULTILINE).finditer
_iter_css_urls = re.compile(r'url\((' + '["][^"]*["]|' + "['][^']*[']|" + r'[^)]*)\)', re.I).finditer
_iter_css_imports = re.compile(r'@import "(.*?)"').finditer
_archive_re = re.compile(r'[^ ]+')
_parse_meta_refresh_url = re.compile(r'[^;=]*;\s*(?:url\s*=\s*)?(?P<url>.*)$', re.I).search


def unquote_match(s, pos):
    if s[:1] == '"' and s[-1:] == '"' or s[:1] == "'" and s[-1:] == "'" or \
            s[:1] == '"' and s[-1:] == "'" or s[:1] == "'" and s[-1:] == '"':
        return s[1:-1], pos + 1
    else:
        return s, pos


class ElementBase(etree.ElementBase):
    def remove_csrf_checks(self):
        # Remove integrity or cors check from the file
        self.attrib.pop('integrity', None)
        self.attrib.pop('crossorigin', None)

    def replace_url(self, old_url, new_url, attr, pos):
        # Change the url in the object depending on the  case
        if not isinstance(new_url, string_types):
            TypeError("Expected %r, got %r" % (string_types, new_url))
        if not isinstance(pos, integer_types):
            TypeError("Expected %r, got %r" % (integer_types, pos))
        if new_url is None or new_url == old_url:
            return
        if attr is None:
            new = self.text[:pos] + new_url + self.text[pos + len(old_url):]
            self.text = new
        else:
            cur = self.get(attr)
            if not pos and len(cur) == len(old_url):
                new = new_url  # most common case
            else:
                new = cur[:pos] + new_url + cur[pos + len(old_url):]
            self.set(attr, new)
        #: For the new url to work properly we need to remove
        #: any sort of url check attributes present in element.
        self.remove_csrf_checks()


def iterparse(source, encoding=None, events=None,
              include_meta_charset_tag=False, **kwargs):
    """Incrementally parse HTML document into ElementTree.

    TODO:
        1. Make iterparse function take in a factory argument which
            defines the output of the generator.
        2. Modify the links function to be a subclass of Iterator
            and it should be passable to iterparse as factory arg.
        3. Make a additional no-op iterator and a forms iterator.

    """
    encoding = encoding or 'iso-8859-1'  # rfc default web encoding
    parser = etree.HTMLPullParser(events=events, encoding=encoding, **kwargs)
    lookup = etree.ElementDefaultClassLookup(ElementBase)
    parser.set_element_class_lookup(lookup)

    def iterator():
        # try:
        while True:
            # yield from chain.from_iterable(map(filter_, parser.read_events()))
            # for i in chain.from_iterable(
            #   (links(element) for event, element in parser.read_events())
            # ):
            #     yield i
            for event, element in parser.read_events():
                for child in links(element):
                    if child is None:
                        continue
                    yield child
            data = source.read(0o3000)
            if not data:
                break
            parser.feed(data)

        if include_meta_charset_tag:
            parser.feed(('<meta charset="%s" />' % encoding).encode(
                encoding, 'xmlcharrefreplace'))
            # try:
            #     head = root.xpath(
            #         "descendant-or-self::head|descendant-or-self::x:head",
            #         namespaces={'x': XHTML_NAMESPACE}
            #     )[0]
            # except (AttributeError, IndexError):
            #     head = parser.makeelement('head')
            #     root.insert(0, head)
            # #: Write the inferred charset to the html dom so that browsers read this
            # #: document in our specified encoding.
            # head.insert(0, parser.makeelement('meta', charset=encoding))
        try:
            it.root = parser.close()
        except etree.XMLSyntaxError:
            parser.feed(
                '<html></html>'.encode(encoding, 'xmlcharrefreplace'))
            it.root = parser.close()

        # parser could generate end events for html and
        # body tags which the parser itself inserted.
        # for event, element in parser.read_events():
        #     for child in links(element):
        #         if child is None:
        #             continue
        #         yield child

        # it.root = root
        # noinspection PyUnusedLocal
        # root = None
        # XXX No implicit source closing
        # if close_source:
        #     source.close()

    class IterParseIterator(Iterator):
        next = __next__ = functools.partial(next, iterator())

    it = IterParseIterator()
    it.root = None
    del IterParseIterator

    # close_source = False
    if not hasattr(source, "read"):
        # source = open(source, "rb")
        # close_source = True
        raise TypeError("Expected a readable object, got %r" % source)

    return it


def links(el):
    tag = _nons(el.tag)
    attribs = el.attrib

    if tag == 'object':  # pragma: no cover
        codebase = None
        if 'codebase' in attribs:
            codebase = el.get('codebase')
            yield el, 'codebase', codebase, 0
        for attrib in ('classid', 'data'):
            if attrib in attribs:
                value = el.get(attrib)
                if codebase is not None:
                    value = urljoin(codebase, value)
                yield el, attrib, value, 0
        if 'archive' in attribs:
            for match in _archive_re.finditer(el.get('archive')):
                value = match.group(0)
                if codebase is not None:
                    value = urljoin(codebase, value)
                yield el, 'archive', value, match.start()
    else:
        for attrib in link_attrs:
            if attrib in attribs:
                yield el, attrib, attribs[attrib], 0

        # XXX Patch for src-set url detection
        for attrib in srcset_attrs:
            if attrib in attribs:
                urls = list(_iter_srcset_urls(attribs[attrib]))
                if urls:
                    # yield in reversed order to simplify in-place modifications
                    for match in urls[::-1]:
                        url, start = unquote_match(match.group(1).strip(), match.start(1))
                        yield el, attrib, url, start
    if tag == 'meta':
        http_equiv = attribs.get('http-equiv', '').lower()
        if http_equiv == 'refresh':
            content = attribs.get('content', '')
            match = _parse_meta_refresh_url(content)
            url = (match.group('url') if match else content).strip()
            # unexpected content means the redirect won't work, but we might
            # as well be permissive and yield the entire string.
            if url:
                url, pos = unquote_match(
                    url, match.start('url') if match else content.find(url))
                yield el, 'content', url, pos
        itemprop = attribs.get('itemprop', '').lower()
        if itemprop == 'image':
            url = attribs.get('content', '')
            if url:
                yield el, 'content', url, 0
    elif tag == 'param':
        valuetype = el.get('valuetype') or ''
        if valuetype.lower() == 'ref':
            yield el, 'value', el.get('value'), 0
    elif tag == 'script' and el.text:
        urls = [
            # (start_pos, url)
            unquote_match(match.group(1), match.start(1))[::-1]
            for match in _iter_css_urls(el.text)
        ]
        if urls:
            # sort by start pos to bring both match sets back into order
            # and reverse the list to report correct positions despite
            # modifications
            urls.sort(reverse=True)
            for start, url in urls:
                yield el, None, url, start
    elif tag == 'style' and el.text:
        urls = [
                   # (start_pos, url)
                   unquote_match(match.group(1), match.start(1))[::-1]
                   for match in _iter_css_urls(el.text)
               ] + [
                   (match.start(1), match.group(1))
                   for match in _iter_css_imports(el.text)
               ]
        if urls:
            # sort by start pos to bring both match sets back into order
            # and reverse the list to report correct positions despite
            # modifications
            urls.sort(reverse=True)
            for start, url in urls:
                yield el, None, url, start
    if 'style' in attribs:
        urls = list(_iter_css_urls(attribs['style']))
        if urls:
            # yield in reversed order to simplify in-place modifications
            for match in urls[::-1]:
                url, start = unquote_match(match.group(1), match.start(1))
                yield el, 'style', url, start


# HTML style and script tags cleaner
cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True


class MultiParser(object):  # pragma: no cover
    """Provides apis specific to scraping or data searching purposes.

    This contains the apis from the requests-html module.

    Most of the source code is from the MIT Licensed library called
    `requests-html` courtesy of kenneth, some code has been heavily modified to
    fit the needs of this project but some apis are still untouched.

    :param html: html markup string.
    :param encoding: optional explicit declaration of encoding type of that web page
    :param element: Used internally: PyQuery object or raw html.
    """

    def __init__(self, html=None, encoding=None, element=None):
        self._lxml = None
        self._pq = None
        self._soup = None
        self._html = html  # represents your raw html
        self._encoding = encoding  # represents your provided encoding
        self.element = element  # internal lxml element
        self._decoded_html = False  # internal switch to tell if html has been decoded
        self.default_encoding = 'iso-8859-1'  # a standard encoding defined by w3c

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
        resp = requests.request(method, url, stream=True, **params)
        resp.raise_for_status()
        self._html = resp.content

    def get(self, url, **params):
        return self.request('GET', url, **params)

    def post(self, url, **params):
        return self.request('POST', url, **params)

    def get_forms(self):
        """Returns a list of form elements available on the page."""
        return fromstring(
            self.html
        ).xpath(
            "descendant-or-self::form|descendant-or-self::x:form",
            namespaces={'x': XHTML_NAMESPACE}
        )

    def submit_form(self, form, url=None, **extra_values):
        """
        Helper function to submit a form.

        .. todo::
            check documentation.

        You can use this like::

            wp = WebPage()
            wp.get('http://httpbin.org/forms/')
            form = wp.get_forms()[0]
            form.inputs['email'].value = 'bar' # etc
            form.inputs['password'].value = 'baz' # etc
            wp.submit_form(form)
            wp.get_links()

        The action is one of 'GET' or 'POST', the URL is the target URL as a
        string, and the values are a sequence of ``(name, value)`` tuples with the
        form data.
        """
        values = form.form_values()
        if extra_values:
            if hasattr(extra_values, 'items'):
                extra_values = extra_values.items()
            values.extend(extra_values)

        if url is None:
            if form.action:
                url = form.action
            else:
                url = form.base_url
        return self.request(form.method, url, data=values)

    @property
    def raw_html(self):
        """Bytes representation of the HTML content.
        (`learn more <http://www.diveintopython3.net/strings.html>`_).
        """
        if self._html:
            return self._html
        else:
            return tostring(self.element, encoding=self.encoding)

    @raw_html.setter
    def raw_html(self, html):
        """Property setter for raw_html. Type can be bytes."""
        self._html = html

    @property
    def html(self):
        """Unicode representation of the HTML content."""
        if self._html:
            return self.decode()
        else:
            return tostring(self.element, encoding='unicode')

    @html.setter
    def html(self, html):
        """Property setter for self.html"""
        if not isinstance(html, str):
            raise TypeError
        self._html = html
        self.decode()

    def encode(self, encoding=None, errors='xmlcharrefreplace'):
        """Returns the html encoded with specified encoding."""
        return self.html.encode(encoding=encoding, errors=errors)

    def decode(self):
        """Decodes the html set to this object and returns used encoding and decoded html."""
        self._encoding, html = self.decode_html(self._html, self._encoding, self.default_encoding)
        return html

    @staticmethod
    def decode_html(html_string, encoding=None, default_encoding='iso-8859-1'):
        """Decodes a html string into a unicode string.
        If explicit encoding is defined then
        it would use it otherwise it will decoding it using
        beautiful soups UnicodeDammit feature,
        otherwise it will use w3lib to decode the html.

        Returns a two tuple with (<encoding>, <decoded unicode string>)

        :rtype: (str, str)
        :returns: (used-encoding, unicode-markup)
        """

        tried = [encoding, default_encoding]

        try:
            logger.info("Trying UnicodeDammit Codec for decoding html.")
            try:
                import bs4
            except ImportError:
                raise ImportError(
                    "bs4 module is not installed. "
                    "Install it using pip: $ pip install bs4"
                )
            converted = bs4.UnicodeDammit(html_string, [encoding], is_html=True)

            if not converted.unicode_markup:
                tried += converted.tried_encodings
                logger.critical(
                    "UnicodeDammit decoder failed to decode html!"
                    "Encoding tried by default enc: [%s]"
                    "Trying fallback..." % ','.join(tried)
                )
                raise UnicodeDecodeError

            return converted.original_encoding, converted.unicode_markup

        except (UnicodeDecodeError, ImportError):
            # This method will definitely decode the html though
            # the result could be corrupt. But if you getting a
            # corrupt html output then you definitely have to
            # manually provide the encoding.
            try:
                import w3lib
                from w3lib.encoding import html_to_unicode
            except ImportError:
                raise ImportError(
                    "w3lib module is not installed. "
                    "Install it using pip: $ pip install w3lib"
                )

            enc, unc = w3lib.encoding.html_to_unicode(
                None, html_body_str=html_string,
                default_encoding=default_encoding
            )
            return enc, unc

    @property
    def encoding(self):
        """The encoding string to be used, extracted from the HTML and
        :class:`HTMLResponse <HTMLResponse>` headers.
        """
        if self._encoding is None:
            self.decode()
        return self._encoding

    @encoding.setter
    def encoding(self, enc):
        """Property setter for self.encoding."""
        self._encoding = enc

    @property
    def lxml(self):
        """Parses the decoded self.html contents after decoding it by itself
        decoding detector (default) or decoding it using provided self.default_encoding.
        """
        if self._lxml is None:
            self._lxml = fromstring(self.html)
        return self._lxml

    @property
    def bs4(self):
        """BeautifulSoup object under the hood.
        Read more about beautiful_soup at https://www.crummy.com/software/BeautifulSoup/doc
        """
        try:
            import bs4
        except ImportError:
            raise ImportError(
                "bs4 module is not installed. "
                "Install it using pip: $ pip install bs4"
            )
        if self._soup is None:
            self._soup = bs4.BeautifulSoup(self.raw_html, 'lxml')
        return self._soup

    @property
    def pq(self):
        """`PyQuery <https://pythonhosted.org/pyquery/>`_ representation
        of the :class:`Element <Element>` or :class:`HTML <HTML>`.
        """
        try:
            import pyquery
        except ImportError:
            raise ImportError(
                "pyquery module is not installed. "
                "Install it using pip: $ pip install pyquery"
            )
        if self._pq is None:
            self._pq = pyquery.PyQuery(self.lxml)

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
            Element(element=found, default_encoding=encoding)
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
                element.raw_html = tostring(cleaner.clean_html(element.lxml))
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
            Element(element=selection, default_encoding=_encoding or self.encoding)
            if inspect.isclass(selection) and not issubclass(selection, str) else str(selection)
            for selection in selected
        ]

        # Sanitize the found HTML.
        if clean:
            elements_copy = list(elements)
            elements = []

            for element in elements_copy:
                element.raw_html = tostring(cleaner.clean_html(element.lxml))
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
        try:
            import parse
        except ImportError:
            raise ImportError(
                "parse module is not installed. "
                "Install it using pip: $ pip install parse"
            )
        return parse.search(template, self.html)

    def search_all(self, template):
        """Search the :class:`Element <Element>` (multiple times) for the given parse
        template.

        :param template: The Parse template to use.
        """
        if not isinstance(template, str):
            raise TypeError("Expected string, got %r" % type(template))
        try:
            import parse
        except ImportError:
            raise ImportError(
                "parse module is not installed. "
                "Install it using pip: $ pip install parse"
            )
        return [r for r in parse.findall(template, self.html)]


class Element(MultiParser):  # pragma: no cover
    """An element of HTML.

    :param element: The element from which to base the parsing upon.
    :param default_encoding: Which encoding to default to.
    """

    def __init__(self, element, default_encoding=None):
        super(Element, self).__init__(element=element, encoding=default_encoding)
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
            d = {}
            for k, v in self.element.items():
                d[k] = v
            self._attrs = d

            # Split class and rel up, as there are usually many of them:
            for attr in ['class', 'rel']:
                if attr in self._attrs:
                    self._attrs[attr] = tuple(self._attrs[attr].split())

        return self._attrs
