# Copyright 2019; Raja Tomar
import unittest

import lxml.etree
from lxml.html import Element
from lxml.html import tostring
from six import BytesIO
from six import StringIO
from six import next
from six.moves.collections_abc import Iterator

from pywebcopy.parsers import iterparse
from pywebcopy.parsers import links
import pywebcopy.parsers


class TestIterParse(unittest.TestCase):

    def test_source_is_empty_string(self):
        with self.assertRaises(TypeError):
            iterparse('')

    def test_source_without_read_method(self):
        with self.assertRaises(TypeError):
            iterparse(object())
        with self.assertRaises(TypeError):
            iterparse(None)

    def test_source_is_not_bytes(self):
        source = StringIO('<img src="#">')
        context = iterparse(source)
        lst = list(context)
        self.assertTrue(len(lst) == 1)
        el, attr, url, pos = lst.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src')
        self.assertEqual(el.tag, 'img')
        self.assertEqual(el.attrib, {'src': '#'})

    def test_source_is_empty(self):
        source = BytesIO(b'')
        context = iterparse(source)
        self.assertEqual(list(context), [])
        self.assertEqual(tostring(context.root),
                         b'<html></html>')

    def test_meta_charset_insertion(self):
        context = iterparse(BytesIO(b''), include_meta_charset_tag=True)
        self.assertEqual(list(context), [])
        elms = context.root.xpath('//meta')
        self.assertEqual(len(elms), 1)
        meta = elms.pop()
        self.assertEqual(meta.tag, 'meta')
        self.assertEqual(meta.attrib['charset'], 'iso-8859-1')
        self.assertEqual(tostring(meta),
                         tostring(lxml.html.Element('meta', charset='iso-8859-1')))
        self.assertEqual(
            tostring(context.root),
            b'<html><head>%s</head></html>' % tostring(meta))

    def test_return_type(self):
        source = BytesIO(b'<img src="#">')
        context = iterparse(source)
        self.assertTrue(isinstance(context, Iterator))

    def test_root_pre_iteration(self):
        source = BytesIO(b'<img src="#">')
        context = iterparse(source)
        self.assertTrue(hasattr(context, 'root'))
        self.assertTrue(context.root is None)

    def test_root_post_iteration(self):
        source = BytesIO(b'<img src="#">')
        context = iterparse(source)
        list(context)   # consume the generator
        self.assertTrue(context.root is not None)
        self.assertTrue(isinstance(context.root, lxml.etree._Element))

    def test_single_element(self):
        source = BytesIO(b'<img src="#">')
        context = iterparse(source)
        elements = list(context)   # consume the generator
        self.assertTrue(len(elements) == 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src')
        self.assertEqual(el.tag, 'img')
        self.assertEqual(el.attrib, {'src': '#'})

    def test_multi_element(self):
        source = BytesIO(b'<img src="#"><img src="#2">')
        context = iterparse(source)
        elements = list(context)   # consume the generator
        self.assertTrue(len(elements) == 2)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#2')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src')
        self.assertEqual(el.tag, 'img')
        self.assertEqual(el.attrib, {'src': '#2'})
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src')
        self.assertEqual(el.tag, 'img')
        self.assertEqual(el.attrib, {'src': '#'})


class TestElementBase(unittest.TestCase):

    def test_remove_csrf_checks(self):
        token = 'token'
        e = pywebcopy.parsers.ElementBase('link')
        e.set('href', '#')
        e.set('crossorigin', token)
        self.assertEqual(e.attrib.get('crossorigin'), token)
        e.remove_csrf_checks()
        self.assertEqual(e.attrib.get('crossorigin'), None)

    def test_replace_url_in_attrib(self):
        e = pywebcopy.parsers.ElementBase('link')
        url = '#'
        e.set('href', url)
        e.set('crossorigin', 'hash')
        e.replace_url(url, 'new', 'href', 0)
        self.assertEqual(e.attrib.get('href'), 'new')
        self.assertEqual(e.attrib.get('crossorigin'), None)

    def test_replace_url_in_text(self):
        e = pywebcopy.parsers.ElementBase('style')
        url = '"#"'
        e.text = 'html {background: url(%s);}' % url
        e.replace_url(url, '"new"', None, 22)
        self.assertEqual(e.text, 'html {background: url("new");}')

    def test_replace_url_in_style_tag(self):
        e = pywebcopy.parsers.ElementBase('style')
        e.text = """
        @font-face {
        font-family:'fontawesome';
        src:url('../lib/fonts/fontawesome.eot?14663396#iefix') format('embedded-opentype'),
        url('../lib/fonts/fontawesome.woff?14663396') format('woff'),
        url('../lib/fonts/fontawesome.ttf?14663396') format('truetype'),
        url('../lib/fonts/fontawesome.svg?14663396#fontawesome') format('svg');
        font-style:normal;
        }
        """
        # ALWAYS REPLACE THE LAST ONE FIRST
        e.replace_url('../lib/fonts/fontawesome.svg?14663396#fontawesome', '#', None, 305)
        self.assertEqual(e.text, """
        @font-face {
        font-family:'fontawesome';
        src:url('../lib/fonts/fontawesome.eot?14663396#iefix') format('embedded-opentype'),
        url('../lib/fonts/fontawesome.woff?14663396') format('woff'),
        url('../lib/fonts/fontawesome.ttf?14663396') format('truetype'),
        url('#') format('svg');
        font-style:normal;
        }
        """)


class TestLinkSearcher(unittest.TestCase):
    def test_raise_error_on_invalid_argument(self):
        with self.assertRaises(AttributeError):
            list(links(''))

    def test_img_element(self):
        source = Element('img', {'src': '#'})
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src')
        self.assertEqual(el.tag, 'img')
        self.assertEqual(el.attrib, {'src': '#'})

    def test_img_element_without_url(self):
        source = Element('img')
        elements = list(links(source))
        self.assertEqual(len(elements), 0)

    def test_anchor_element(self):
        source = Element('a', {'href': '#'})
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.tag, 'a')
        self.assertEqual(el.attrib, {'href': '#'})

    def test_anchor_element_without_url(self):
        source = Element('a')
        elements = list(links(source))
        self.assertEqual(len(elements), 0)

    def test_link_element(self):
        source = Element('link', {'href': '#'})
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.tag, 'link')
        self.assertEqual(el.attrib, {'href': '#'})

    def test_link_element_without_url(self):
        source = Element('link')
        elements = list(links(source))
        self.assertEqual(len(elements), 0)

    def test_script_element(self):
        source = Element('script', {'src': '#'})
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src')
        self.assertEqual(el.tag, 'script')
        self.assertEqual(el.attrib, {'src': '#'})

    def test_script_element_without_url(self):
        source = Element('script')
        source.text = 'console.log(hello);'
        elements = list(links(source))
        self.assertEqual(len(elements), 0)

    def test_script_element_with_url_in_the_text(self):
        source = Element('script')
        source.text = 'var background = "url(\'image.jpg\')"'
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, 'image.jpg')
        self.assertEqual(pos, 23)
        self.assertEqual(attr, None)
        self.assertEqual(el.tag, 'script')
        self.assertEqual(el.attrib, {})

    def test_form_element(self):
        source = Element('form', {'action': '#'})
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'action')
        self.assertEqual(el.tag, 'form')
        self.assertEqual(el.attrib, {'action': '#'})

    def test_form_element_without_action_url(self):
        source = Element('form')
        elements = list(links(source))
        self.assertEqual(len(elements), 0)

    def test_meta_refresh_element(self):
        source = Element('meta', {'http-equiv': 'refresh', 'content': '#'})
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'content')
        self.assertEqual(el.tag, 'meta')
        self.assertEqual(el.attrib, {'http-equiv': 'refresh', 'content': '#'})

    def test_meta_refresh_element_without_content_url(self):
        source = Element('meta', {'http-equiv': 'refresh'})
        elements = list(links(source))
        self.assertEqual(len(elements), 0)

    def test_html_style_tag_css_url(self):
        source = Element('style')
        source.text = 'html {background: url(#);}'
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 22)
        self.assertEqual(attr, None)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(el.attrib, {})

    def test_html_style_tag_font_face(self):
        source = Element('style')
        source.text = """
        @font-face {
        font-family:'fontawesome';
        src:url('../lib/fonts/fontawesome.eot?14663396#iefix') format('embedded-opentype'),
        url('../lib/fonts/fontawesome.woff?14663396') format('woff'),
        url('../lib/fonts/fontawesome.ttf?14663396') format('truetype'),
        url('../lib/fonts/fontawesome.svg?14663396#fontawesome') format('svg');
        font-style:normal;
        }
        """
        elements = list(links(source))
        self.assertEqual(len(elements), 4)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '../lib/fonts/fontawesome.eot?14663396#iefix')
        self.assertEqual(pos, 74)
        self.assertEqual(attr, None)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(el.attrib, {})
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '../lib/fonts/fontawesome.woff?14663396')
        self.assertEqual(pos, 162)
        self.assertEqual(attr, None)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(el.attrib, {})
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '../lib/fonts/fontawesome.ttf?14663396')
        self.assertEqual(pos, 232)
        self.assertEqual(attr, None)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(el.attrib, {})
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '../lib/fonts/fontawesome.svg?14663396#fontawesome')
        self.assertEqual(pos, 305)
        self.assertEqual(attr, None)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(el.attrib, {})

    def test_html_style_tag_css_url_with_colons(self):
        source = Element('style')
        source.text = 'html {background: url("#");}'
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 23)
        self.assertEqual(attr, None)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(el.attrib, {})

    def test_html_style_tag_css_url_with_altering_colons(self):
        source = Element('style')
        source.text = 'html {background: url("#\');}'
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 23)
        self.assertEqual(attr, None)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(el.attrib, {})

    def test_html_style_tag_css_import(self):
        source = Element('style')
        source.text = '@import url(#);'
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 12)
        self.assertEqual(attr, None)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(el.attrib, {})

    def test_html_style_tag_css_import_without_url(self):
        source = Element('style')
        source.text = '@import fonts;'
        elements = list(links(source))
        self.assertEqual(len(elements), 0)

    def test_inline_css_url(self):
        source = Element('div', {'style': 'background: url("#");'})
        elements = list(links(source))
        self.assertEqual(len(elements), 1)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, '#')
        self.assertEqual(pos, 17)
        self.assertEqual(attr, 'style')
        self.assertEqual(el.tag, 'div')
        self.assertEqual(el.attrib, {'style': 'background: url("#");'})

    def test_img_src_set_attribute_standard(self):
        source = Element('img', {'src-set': 'img1 1x, img2 2x,'})
        elements = list(links(source))
        self.assertEqual(len(elements), 2)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, 'img1')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src-set')
        self.assertEqual(el.tag, 'img')
        self.assertEqual(el.attrib, {'src-set': 'img1 1x, img2 2x,'})
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, 'img2')
        self.assertEqual(pos, 9)
        self.assertEqual(attr, 'src-set')
        self.assertEqual(el.tag, 'img')
        self.assertEqual(el.attrib, {'src-set': 'img1 1x, img2 2x,'})

    def test_img_src_set_attribute_bad_formatted(self):
        source = Element('img', {'src-set': 'img1 1x; img2 2x,'})
        elements = list(links(source))
        self.assertEqual(len(elements), 2)
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, 'img1')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src-set')
        self.assertEqual(el.tag, 'img')
        self.assertEqual(el.attrib, {'src-set': 'img1 1x; img2 2x,'})
        el, attr, url, pos = elements.pop()
        self.assertEqual(url, 'img2')
        self.assertEqual(pos, 9)
        self.assertEqual(attr, 'src-set')
        self.assertEqual(el.tag, 'img')
        self.assertEqual(el.attrib, {'src-set': 'img1 1x; img2 2x,'})


html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="3;http://nx-domain.com/redirect">
<link rel="stylesheet" href="css/main.css">
<link rel="stylesheet" href="http://nx-domain.com/css/style.css">
<style>
@import "css/theme.css";
body {background: url("img/background.png");}
</style>
</head>
<body>
<a href="#"></a>
<a href="javascript:void(0);"></a>
<a href="http://new-site.com"></a>
<div style="background: url('img/background.png');"></div>
<img src="img/img1.png" alt="img1-alt"/>
<img src="http://static-site.com/img/img3.png" alt=""/>
</body>
</html>
"""


class TestFullHTMLParsing(unittest.TestCase):

    # Single instance of the parser to avoid creating anew each time.
    context = iterparse(BytesIO(html.encode('utf-8')))

    # NOTE: Methods are ordered in the sequence they will be parsed

    def test_a_first_meta_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'meta')
        self.assertEqual(url, 'http://nx-domain.com/redirect')
        self.assertEqual(pos, 2)
        self.assertEqual(attr, 'content')
        self.assertEqual(el.attrib, {'http-equiv': 'refresh', 'content': "3;http://nx-domain.com/redirect"})

    def test_b_first_link_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'link')
        self.assertEqual(url, 'css/main.css')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.attrib, {'rel': 'stylesheet', 'href': "css/main.css"})

    def test_c_second_link_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'link')
        self.assertEqual(url, 'http://nx-domain.com/css/style.css')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.attrib, {'rel': 'stylesheet', 'href': 'http://nx-domain.com/css/style.css'})

    def test_d_style_tag_css_url_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(url, "img/background.png")
        self.assertEqual(pos, 49)
        self.assertEqual(attr, None)
        self.assertEqual(el.attrib, {})

    def test_e_style_tag_css_import_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(url, "css/theme.css")
        self.assertEqual(pos, 10)
        self.assertEqual(attr, None)
        self.assertEqual(el.attrib, {})

    def test_f_first_anchor_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'a')
        self.assertEqual(url, "#")
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.attrib, {'href': '#'})

    def test_g_second_anchor_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'a')
        self.assertEqual(url, "javascript:void(0);")
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.attrib, {'href': "javascript:void(0);"})

    def test_h_third_anchor_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'a')
        self.assertEqual(url, "http://new-site.com")
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.attrib, {'href': "http://new-site.com"})

    def test_i_inline_style_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'div')
        self.assertEqual(url, "img/background.png")
        self.assertEqual(pos, 17)
        self.assertEqual(attr, 'style')
        self.assertEqual(el.attrib, {'style': "background: url('img/background.png');"})

    def test_j_first_img_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'img')
        self.assertEqual(url, "img/img1.png")
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src')
        self.assertEqual(el.attrib, {'src': "img/img1.png", 'alt': 'img1-alt'})

    def test_k_second_img_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'img')
        self.assertEqual(url, "http://static-site.com/img/img3.png")
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src')
        self.assertEqual(el.attrib, {'src': "http://static-site.com/img/img3.png", 'alt': ""})

    def test_y_empty_iterator(self):
        with self.assertRaises(StopIteration):
            next(self.context)
        self.assertEqual(len(list(self.context)), 0)

    def test_z_root_tree_attribute(self):
        self.assertTrue(hasattr(self.context.root, 'getroottree'))
        self.assertTrue(isinstance(self.context.root, lxml.etree.ElementBase))
        self.assertTrue(isinstance(self.context.root.getroottree(), lxml.etree._ElementTree))


class TestFullLatin1EncodedHTMLParsing(unittest.TestCase):

    # Single instance of the parser to avoid creating anew each time.
    context = iterparse(
        BytesIO(html.encode('latin1', 'replace')), encoding='latin1')

    # NOTE: Methods are ordered in the sequence they will be parsed

    def test_a_first_meta_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'meta')
        self.assertEqual(url, 'http://nx-domain.com/redirect')
        self.assertEqual(pos, 2)
        self.assertEqual(attr, 'content')
        self.assertEqual(el.attrib, {'http-equiv': 'refresh', 'content': "3;http://nx-domain.com/redirect"})

    def test_b_first_link_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'link')
        self.assertEqual(url, 'css/main.css')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.attrib, {'rel': 'stylesheet', 'href': "css/main.css"})

    def test_c_second_link_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'link')
        self.assertEqual(url, 'http://nx-domain.com/css/style.css')
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.attrib, {'rel': 'stylesheet', 'href': 'http://nx-domain.com/css/style.css'})

    def test_d_style_tag_css_url_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(url, "img/background.png")
        self.assertEqual(pos, 49)
        self.assertEqual(attr, None)
        self.assertEqual(el.attrib, {})

    def test_e_style_tag_css_import_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'style')
        self.assertEqual(url, "css/theme.css")
        self.assertEqual(pos, 10)
        self.assertEqual(attr, None)
        self.assertEqual(el.attrib, {})

    def test_f_first_anchor_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'a')
        self.assertEqual(url, "#")
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.attrib, {'href': '#'})

    def test_g_second_anchor_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'a')
        self.assertEqual(url, "javascript:void(0);")
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.attrib, {'href': "javascript:void(0);"})

    def test_h_third_anchor_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'a')
        self.assertEqual(url, "http://new-site.com")
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'href')
        self.assertEqual(el.attrib, {'href': "http://new-site.com"})

    def test_i_inline_style_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'div')
        self.assertEqual(url, "img/background.png")
        self.assertEqual(pos, 17)
        self.assertEqual(attr, 'style')
        self.assertEqual(el.attrib, {'style': "background: url('img/background.png');"})

    def test_j_first_img_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'img')
        self.assertEqual(url, "img/img1.png")
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src')
        self.assertEqual(el.attrib, {'src': "img/img1.png", 'alt': 'img1-alt'})

    def test_k_second_img_element(self):
        el, attr, url, pos = next(self.context)
        self.assertEqual(el.tag, 'img')
        self.assertEqual(url, "http://static-site.com/img/img3.png")
        self.assertEqual(pos, 0)
        self.assertEqual(attr, 'src')
        self.assertEqual(el.attrib, {'src': "http://static-site.com/img/img3.png", 'alt': ""})

    def test_y_empty_iterator(self):
        with self.assertRaises(StopIteration):
            next(self.context)
        self.assertEqual(len(list(self.context)), 0)

    def test_z_root_tree_attribute(self):
        self.assertTrue(hasattr(self.context.root, 'getroottree'))
        self.assertTrue(isinstance(self.context.root, lxml.etree.ElementBase))
        self.assertTrue(isinstance(self.context.root.getroottree(), lxml.etree._ElementTree))


if __name__ == '__main__':
    unittest.main()
