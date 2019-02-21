# -*- coding: utf-8 -*-
"""
pywebcopy.parsers
~~~~~~~~~~~~~~~~~

Parsing of the html and Element generation factory.

"""
import collections
import re
from datetime import datetime
from functools import lru_cache
from threading import current_thread
from collections import namedtuple

from bs4 import BeautifulSoup
from bs4.dammit import UnicodeDammit
from lxml.etree import Comment, iterparse, parse as etree_parse, HTMLParser
from lxml.html import _unquote_match, _archive_re, _nons, _iter_css_imports, \
    _iter_css_urls, _parse_meta_refresh_url, fromstring, tostring
from lxml.html.clean import Cleaner
from parse import findall, search as parse_search
from pyquery import PyQuery
from six.moves.urllib.parse import urljoin
from six.moves.urllib.request import pathname2url
from w3lib.encoding import html_to_unicode

from . import LOGGER, config as global_config, SESSION
from .elements import LinkTag, AnchorTag, ScriptTag, ImgTag, TagBase
from .exceptions import UrlRefusedByTagHandlerError, UrlTransformerNotSetup
from .globals import SINGLE_LINK_ATTRIBS, VERSION, MARK, LIST_LINK_ATTRIBS
from .urls import relate

utcnow = datetime.utcnow
link_attrs = SINGLE_LINK_ATTRIBS
list_link_attrs = LIST_LINK_ATTRIBS
_iter_srcset_urls = re.compile(r'((?:https?://)?[^\s,]+)[\s]+').finditer

element_map = {
    'link': LinkTag,
    'style': LinkTag,
    'script': ScriptTag,
    'img': ImgTag,
    'a': AnchorTag,
    'form': AnchorTag,
}


class Map(dict):
    """"""
    # __dict__ = element_map


# element_map = Map(**_map)


def register_tag_handler(tag, handler):
    """Register a handler for the specified tag.

    :param tag: the tag for which to register the handler
    :type handler: TagBase, AnchorTag, LinkTag, ImgTag
    :param handler: Tag handler for the tag
    """
    assert isinstance(tag, str), "Tag must of string type."
    assert issubclass(handler, TagBase), "Handler must be subclassed from TagBase."
    element_map[tag] = handler


def deregister_tag_handler(tag):
    """Removes the handler for a specified html tag."""
    assert isinstance(tag, str), "Tag must be of string type."
    element_map.pop(tag, None)


@lru_cache(maxsize=500)
def cached_path2url_relate(target_file, start_file):
    return pathname2url(relate(target_file, start_file))


class BaseIncrementalParser(object):
    """Base Parser which builds tree and generates file elements
    and also handles these file elements.

    :param encoding: Specified encoding type of the provided data.
    """

    def __init__(self, encoding=None):

        self.encoding = encoding
        self.root = None
        self._source = None
        self._stack = set()

        if not global_config.is_set():
            import warnings
            warnings.warn("Global Configuration is not setup. This could lead to "
                          "files being saved at unexpected places.")

    def __repr__(self):
        return '<IncrementalParser: %s>' % current_thread().name

    def __iter__(self):
        if self.root is None:
            self.__parse__()
        return self._stack.__iter__()

    def __len__(self):
        return len(self._stack)

    def files(self, tags=None):
        if self.root is None:
            self.__parse__()

        if not tags:
            for elem in self._stack:
                yield elem
        else:
            if isinstance(tags, str):
                tags = [tags]
            assert isinstance(tags, collections.Iterable), "A iteratable with tag " \
                                                           "strings is required!"

            for elem in self._stack:
                if elem.tag in tags:
                    yield elem

    def __getitem__(self, item):
        assert isinstance(item, str), "Expected str, got %r!" % type(item)
        tag = item.lower().strip()
        return self.files(tag)

    #######################
    # Overrideables
    #######################

    @property
    def utx(self):
        """UrlTransformer dispatch.
        :rtype: UrlTransformer
        """
        raise UrlTransformerNotSetup()

    def get_source(self):
        """Returns the resources set for this object.
        This method can be overridden to provide alternate way of source loading."""
        pass

    def set_source(self, source, encoding=None, base_url=None):
        """Sets up the resource for this object."""
        pass

    #########################
    # Internal Handling
    #########################

    def __create_element__(self, tag, url):
        """Creates a Handler object from the element and url."""

        # create a object depending on tag
        o = element_map.get(tag, TagBase)
        # Populate the object with basic properties
        o = o(url, base_url=self.utx.base_url, base_path=self.utx.base_path)
        o.tag = tag    # A tag specifier is required

        assert self.utx is not None, "Webpage utx not set."
        assert self.utx.file_path is not None, "Webpage file_path is not generated by utx!"
        assert o.file_path is not None, "File Path was not generated by the handler."

        #: Calculate a path relative from the parent Webpage
        o.rel_path = cached_path2url_relate(o.file_path, self.utx.file_path)

        assert o.rel_path is not None, "Relative Path was not generated by the handler."

        return o

    def handle(self, elem, attr, url, pos):
        """Handles elements of the lxml tree and creates files from them.

        Note: Default handler function structures makes use of .rel_path attribute
        which is completely internal and any usage depending on this attribute
        may not work properly.
        """

        # There are internal links present on the html page which are files
        # that includes `#` and `javascript:` and 'data:base64;` type links
        # or a simple `/` anchor
        # thus these links needs to be left as is.
        if url[:1] == u'#' or url[:4] in [u'java', u'data'] or url[1:] == '':
            LOGGER.debug('Url was not valid : %s' % url)
            return

        LOGGER.info('Handling url %s' % url)

        try:
            # Create a new element and handle basic pre-population internally
            obj = self.__create_element__(elem.tag, url)
        except AssertionError as e:
            LOGGER.exception(e)
            return
        except UrlRefusedByTagHandlerError as e:
            LOGGER.exception(e)
            return

        # Remove integrity or cors check from the file
        elem.attrib.pop('integrity', None)
        elem.attrib.pop('crossorigin', None)

        # Change the url in the object depending on the  case
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
        self._stack.add(obj)

    def __parse__(self):
        """
        Yielding and internally handling (element, attribute, link, pos),
        where attribute may be None
        (indicating the link is in the text).  ``pos`` is the position
        where the link occurs; often 0, but sometimes something else in
        the case of links in stylesheets or style tags.

        Note: multiple links inside of a single text string or
        attribute value are returned in reversed order.  This makes it
        possible to replace or delete them from the text string value
        based on their reported text positions.  Otherwise, a
        modification at one text position can change the positions of
        links reported later on.
        """

        assert self.utx is not None, "UrlTranformer not Implemented."  # internal error
        assert self.utx.base_path is not None, "Base Path is not set!"
        assert self.utx.base_url is not None, "Base url is not Set!"

        source = self.get_source()

        assert source is not None, "Source is not Set!"
        assert hasattr(source, 'read'), "File like object is required!"

        parser = HTMLParser(encoding=self.encoding,
                            collect_ids=False,
                            huge_tree=True,
                            recover=False)
        context_tree = etree_parse(source, parser=parser)

        del source
        del parser

        # The tree generated by the parse is stored in the self.root
        # variable and can be utilised further for any number of use cases
        self.root = context_tree.getroot()

        # WaterMarking :)
        self.root.insert(0, Comment(MARK.format('', VERSION, self.utx.url, utcnow(), '')))

        # Modify the tree elements
        for el in context_tree.iter():
            self.__handle(el)

    def __handle(self, el):
        """Handles a lxml element which is straight out of the parser
        and does the work of file objects building and starts the download.
        """
        attribs = el.attrib
        tag = _nons(el.tag)
        if tag == 'object':
            codebase = None
            if 'codebase' in attribs:
                codebase = el.get('codebase')
                self.handle(el, 'codebase', codebase, 0)
            for attrib in ('classid', 'data'):
                if attrib in attribs:
                    value = el.get(attrib)
                    if codebase is not None:
                        value = urljoin(codebase, value)
                    self.handle(el, attrib, value, 0)
            if 'archive' in attribs:
                for match in _archive_re.finditer(el.get('archive')):
                    value = match.group(0)
                    if codebase is not None:
                        value = urljoin(codebase, value)
                    self.handle(el, 'archive', value, match.start())
        else:
            for attrib in link_attrs:
                if attrib in attribs:
                    self.handle(el, attrib, attribs[attrib], 0)
            for attrib in list_link_attrs:
                if attrib in attribs:
                    urls = list(_iter_srcset_urls(attribs[attrib]))
                    if urls:
                        # return in reversed order to simplify in-place modifications
                        for match in urls[::-1]:
                            url, start = _unquote_match(match.group(1).strip(), match.start(1))
                            self.handle(el, attrib, url, start)
        if tag == 'meta':
            http_equiv = attribs.get('http-equiv', '').lower()
            if http_equiv == 'refresh':
                content = attribs.get('content', '')
                match = _parse_meta_refresh_url(content)
                url = (match.group('url') if match else content).strip()
                # unexpected content means the redirect won't work, but we might
                # as well be permissive and return the entire string.
                if url:
                    url, pos = _unquote_match(
                        url, match.start('url') if match else content.find(url))
                    self.handle(el, 'content', url, pos)
        elif tag == 'param':
            valuetype = el.get('valuetype') or ''
            if valuetype.lower() == 'ref':
                self.handle(el, 'value', el.get('value'), 0)
        elif tag == 'style' and el.text:
            urls = [
                       # (start_pos, url)
                       _unquote_match(match.group(1), match.start(1))[::-1]
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
                    self.handle(el, None, url, start)
        if 'style' in attribs:
            urls = list(_iter_css_urls(attribs['style']))
            if urls:
                # return in reversed order to simplify in-place modifications
                for match in urls[::-1]:
                    url, start = _unquote_match(match.group(1), match.start(1))
                    self.handle(el, 'style', url, start)


# HTML style and script tags cleaner
cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True


class MultiParser(object):
    """Provides apis specific to scraping or data searching purposes.

    This contains the apis from the requests-html module.

    Most of the source code is from the MIT Licensed library called
    `requests-html` courtesy of kenneth, some code has been heavily modified to
    fit the needs of this project but some apis are still untouched.

    :param HTML: html markup string.
    :param encoding: optional explicit declaration of encoding type of that webpage
    :param element: Used internally: PyQuery object or raw html.
    """

    def __init__(self, HTML=None, encoding=None, element=None):
        self._lxml = None
        self._pq = None
        self._soup = None
        self._html = HTML                     # represents your raw html
        self._encoding = encoding             # represents your provided encoding
        self.element = element                # internal lxml element
        self._decoded_html = False            # internal switch to tell if html has been decoded
        self.default_encoding = 'iso-8859-1'  # a standard encoding defined by wwwc

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
    def raw_html(self, HTML):
        """Property setter for raw_html. Type can be bytes."""
        self._html = HTML

    @property
    def html(self):
        """Unicode representation of the HTML content."""
        if self._html:
            return self.decode()
        else:
            return tostring(self.element, encoding='unicode')

    @html.setter
    def html(self, HTML):
        """Property setter for self.html"""
        if not isinstance(HTML, str):
            raise TypeError
        self._html = HTML
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
            LOGGER.info("Using default Codec on raw_html!")

            converted = UnicodeDammit(html_string, [encoding], is_html=True)

            if not converted.unicode_markup:
                tried += converted.tried_encodings
                raise UnicodeDecodeError

            # self._encoding = converted.original_encoding
            return converted.original_encoding, converted.unicode_markup

        except UnicodeDecodeError:
            try:
                # This method will definitely decode the html though the result could be corrupt.
                # But if you getting a corrupt html output then you definitely have to
                # manually provide the encoding.
                enc, unc = html_to_unicode(None, html_body_str=html_string,
                                           default_encoding=default_encoding)
                # self._encoding = enc
                return enc, unc

            except UnicodeDecodeError:
                LOGGER.exception("Unicode decoder failed to decode html!"
                                 "Encoding tried by default enc: [%s]"
                                 "Trying fallback..." % ','.join(tried))
                raise

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

    def _write_mark(self, text):
        """Writes a watermark comment in the parsed html."""
        if self.lxml is not None:
            self.lxml.insert(0, Comment(text))

    @property
    def bs4(self):
        """BeautifulSoup object under the hood.
        Read more about beautifulsoup at https://www.crummy.com/software/BeautifulSoup/doc
        """
        if self._soup is None:
            self._soup = BeautifulSoup(self.raw_html, 'lxml')
        return self._soup

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
            if not issubclass(selection, str) else str(selection)
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

        return parse_search(template, self.html)

    def search_all(self, template):
        """Search the :class:`Element <Element>` (multiple times) for the given parse
        template.

        :param template: The Parse template to use.
        """
        if not isinstance(template, str):
            raise TypeError("Expected string, got %r" % type(template))

        return [r for r in findall(template, self.html)]


class Element(MultiParser):
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


def parse(url, parser='html5lib', **kwargs):
    """Factory function parses to BeautifulSoup object.
    Parser for the bs4 is defaulted to 'html5lib'.

    Example:
    >>> parsed_html = parse('http://some-site.com/')
    """
    return BeautifulSoup(SESSION.get(url).content, features=parser, **kwargs)


def parse_content(content, parser='html5lib', **kwargs):
    """Returns the parsed content from provided markup.

    Example:
        >>> parsed_html = parse_content('<html><body>Hello!</body></html>')
    """
    return BeautifulSoup(content, features=parser, **kwargs)
