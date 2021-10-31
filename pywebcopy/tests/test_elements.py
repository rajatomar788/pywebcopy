# Copyright 2020; Raja Tomar
# See license for more details
import os.path
import shutil
import unittest
import tempfile

from pywebcopy.elements import make_fd


class TestFileDescriptorMaking(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.join(tempfile.gettempdir(), 'make_fd_test_dir')

    def tearDown(self):
        shutil.rmtree(self.base_dir)

    def test_standard_fd_return(self):
        fd = make_fd(os.path.join(self.base_dir, 'standard_fd_return'))
        self.assertNotEqual(fd, -1)
        os.close(fd)

    def test_making_dirs(self):
        ans = os.path.join(self.base_dir, 'file')
        fd = make_fd(ans)
        self.assertNotEqual(fd, -1)
        self.assertTrue(os.path.exists(self.base_dir))
        self.assertTrue(os.path.exists(ans))
        os.close(fd)

    def test_making_base_dirs_of_file(self):
        ans = os.path.join(self.base_dir, 'file')
        self.assertFalse(os.path.exists(self.base_dir))
        self.assertFalse(os.path.exists(ans))
        fd = make_fd(ans)
        self.assertNotEqual(fd, -1)
        self.assertTrue(os.path.exists(self.base_dir))
        self.assertTrue(os.path.exists(ans))
        os.close(fd)


from six.moves.SimpleHTTPServer import SimpleHTTPRequestHandler

# import unittest
#
# from six import BytesIO
# from requests import Response
#
#
# html = """
# <!DOCTYPE html>
# <html lang="en"><head>
#     <meta charset="UTF-8">
#     <link rel="stylesheet" href="css/main.css">
#     <link rel="stylesheet" href="http://files.cdn/css/style.css">
#     <style>
#         @import "css/theme.css";
#         body {background: url("img/background.png");}
#     </style>
# </head><body>
# <a href="#"><a href="javascript:void(0);"><a href="http://new-site.com">
# <div style="background: url("img/background.png");">
# <img src="img/img1.png" alt=""><img src="http://other-site.com/img/img3.png" alt="">
# </body>
# </html>
# """
#
#
# class TestParser(unittest.TestCase):
#     def setUp(self):
#         self.p = pywebcopy.Parser()
#
#     def test_file_like_object_source(self):
#         self.p.set_source(io.BytesIO())
#         self.assertTrue(self.p._source)
#
#     def test_bad_source(self):
#         with self.assertRaises(exc.ParseError):
#             self.p.set_source(str)
#             self.p.set_source('')
#
#     def test_source_loading(self):
#         stream = io.BytesIO()
#         self.p._source = stream
#         self.assertEqual(self.p.get_source(), stream)
#
#     def test_bad_source_loading(self):
#         self.p._source = ''
#         with self.assertRaises(exc.ParseError):
#             self.p.get_source()
#
#     def test_bad_source_loading_2(self):
#         self.p._source = object()
#         with self.assertRaises(exc.ParseError):
#             self.p.get_source()
#
#     def test_parsing_source_checks(self):
#         with self.assertRaises(AssertionError):
#             self.p.parse()
#
#
# class TestElementFactory(unittest.TestCase):
#
#     def setUp(self):
#         self.m = elms._ElementFactory()
#
#     def tearDown(self):
#         self.m._element_map = {}
#         self.m = None
#
#     def test_attributes(self):
#         self.assertEqual(self.m._element_map, {})
#         # self.assertEqual(self.m.utx, None)
#
#     def test_register_handler(self):
#         self.assertEqual(self.m._element_map, {})
#         self.m.register_tag_handler('tag', elms.AnchorTag)
#         self.assertNotEqual(self.m._element_map, {})
#         self.assertEqual(self.m._element_map['tag'], elms.AnchorTag)
#
#     def test_deregister_handler(self):
#         self.m.register_tag_handler('tag', elms.AnchorTag)
#         self.assertNotEqual(self.m._element_map, {})
#         self.m.deregister_tag_handler('tag')
#         self.assertEqual(self.m._element_map, {})
#         self.assertEqual(self.m._element_map.get('tag'), None)
#
#     def test_register_handler_bad_handler(self):
#         self.m._element_map = {}
#         with self.assertRaises(AssertionError):
#             self.m.register_tag_handler('new_tag', list)
#         self.assertEqual(self.m._element_map, {})
#
#
# class TestWebPage(unittest.TestCase):
#
#     def setUp(self):
#         self.p = wp.WebPage()
#         self.url = 'http://test-site.com'
#         self.path = tempfile.mkdtemp()
#         self.source = io.StringIO(html)
#         self.file_name = 'index.html'
#         self.utx = urls.URLTransformer(self.url, self.url, self.path, self.file_name)
#
#     def tearDown(self):
#         self.p = None
#         if os.path.exists(self.path):
#             shutil.rmtree(self.path)
#
#     def test_utx_url(self):
#         self.p.utx = self.utx
#         self.assertEqual(self.url, self.p.utx.url)
#
#     def test_utx_base_url(self):
#         self.p.utx = self.utx
#         self.assertEqual(self.url, self.p.utx.base_url)
#
#     def test_utx_base_path(self):
#         self.p.utx = self.utx
#         self.assertEqual(self.path, self.p.utx.base_path)
#
#     def test_utx_file_name(self):
#         self.p.utx = self.utx
#         self.assertEqual(self.file_name, self.p.utx.file_name)
#
#     def test_utx_file_path(self):
#         self.p.utx = self.utx
#         self.assertEqual(
#             os.path.join(self.path, self.utx.to_path, self.file_name),
#             self.p.utx.file_path
#         )
#
#     def test_parsing(self):
#         # self.reset()
#         self.p.set_source(self.source)
#         self.assertTrue(self.p.get_source())
#         self.p.utx = self.utx
#         self.p.parse()
#         # self.assertTrue(self.w.elements)
#         elements = list(self.p.elements)
#         # print(elements)
#         self.assertEqual(len(elements), 7)
#
#     def test_parsing_source_checks(self):
#         # Objective is parsing without any errors
#         self.p.set_source(io.StringIO())
#         self.p.utx = urls.URLTransformer(self.url, self.url, self.path)
#         self.p.parse()
#
#     def test_parsing_without_element_map(self):
#         # self.reset()
#         self.assertEqual(self.p._stack, [])
#         self.p.set_source(self.source)
#         self.p.utx = self.utx
#
#         self.p._element_map = {}
#
#         self.p.parse()
#
#         self.assertEqual(len(self.p.elements), 0)
#
#     def check_connection(self):
#         try:
#             requests.get(self.url)
#         except requests.exceptions.RequestException:
#             return False
#         else:
#             return True
#
#     def test_elements_properties(self):
#         # self.reset()
#         self.p.set_source(self.source)
#         self.p.utx = self.utx
#         self.p.parse()
#
#         for e in self.p.elements:
#             # files must be stored inside project folder
#             self.assertTrue(e.file_path.startswith(self.path))
#             # urls must be absolute
#             self.assertTrue(e.url.startswith('http'))
#             self.assertTrue(os.path.basename(e.file_path))
#
#
# html_2 = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <title>Test</title>
#     <link rel="stylesheet" href="css/main.css">
#     <style>
#         @import url("navigation.css");
#         body {
#             background: url("img/background.png");
#         }
#     </style>
# </head>
# <body>
# <img srcset="img/img_20x14.png 1, img/img_40x14.png 2x">
# <img src="img/img2.png" alt="">
# <img src="img/img3.png" alt="">
# </body>
# </html>"""
#
#
# class TestWebPageElements(unittest.TestCase):
#
#     def setUp(self):
#         self.w = wp.WebPage()
#         self.url = 'http://webpage2.com'
#         self.path = str(tempfile.mkdtemp())
#         self.source = io.StringIO(html_2)
#         self.file_name = 'index.html'
#         self.utx = urls.URLTransformer(self.url, self.url, self.path, self.file_name)
#         self.w.set_source(self.source)
#         self.w.utx = self.utx
#         self.w.parse()
#
#     def tearDown(self):
#         # self.reset()
#         self.w = None
#         self.url = None
#         self.source = None
#         self.file_name = None
#         self.utx = None
#         if os.path.exists(self.path):
#             shutil.rmtree(self.path)
#         self.path = None
#
#     def test_elements(self):
#         self.assertEqual(len(self.w.elements), 7)
#         for e in self.w.elements:
#             self.assertTrue(e.file_path.startswith(self.path))
#             self.assertEqual(self.path, e.base_path)
#             self.assertEqual(self.url, e.base_url)
#             # urls must be absolute
#             self.assertTrue(e.url.startswith('http'))
#             self.assertTrue(len(os.path.basename(e.file_path)) > 0)
#
#
# class TestSubPage(unittest.TestCase):
#
#     def setUp(self):
#         self.url = 'http://test-site.com'
#         self.path = tempfile.mkdtemp()
#         self.file_name = 'index.html'
#         self.utx = cr.SubPage(self.url, self.url, self.path, self.file_name)
#         self.source = io.StringIO(html)
#         self.w = wp.WebPage()
#
#     def tearDown(self):
#         # self.reset()
#         self.w = None
#         self.url = None
#         self.source = None
#         self.file_name = None
#         self.utx = None
#         if os.path.exists(self.path):
#             shutil.rmtree(self.path)
#         self.path = None
#
#     def test_utx_url(self):
#         self.assertEqual(self.url, self.utx.url)
#
#     def test_utx_base_url(self):
#         self.assertEqual(self.url, self.utx.base_url)
#
#     def test_utx_base_path(self):
#         self.assertEqual(self.path, self.utx.base_path)
#
#     def test_utx_file_name(self):
#         self.assertEqual(self.file_name, self.utx.file_name)
#
#     def test_utx_file_path(self):
#         fp = os.path.join(self.path, self.utx.to_path, self.file_name)
#         self.assertEqual(fp, self.utx.file_path)
#
#     def test_run_when_file_exists(self):
#         os.makedirs(os.path.dirname(self.utx.file_path))
#         open(self.utx.file_path, 'x').close()
#         self.assertIsNone(self.utx.run())
#         os.unlink(self.utx.file_path)
#
#     def test_run_host_is_different(self):
#         self.utx.url = 'http://other-host.com'
#         # NOTE: Base URL is still set to self.url
#         self.assertEqual(self.url, self.utx.base_url)
#         self.assertIsNone(self.utx.run())
#
#     def test_sub_page_saving(self):
#         self.w.set_source(self.source)
#         self.w.utx = self.utx
#         self.w.parse()
#         self.utx._sub_page = self.w
#
#         self.utx.run()
#
#
# class TestCrawler(unittest.TestCase):
#
#     def setUp(self):
#         self.w = cr.Crawler()
#         self.url = 'http://webpage2.com'
#         self.path = tempfile.mkdtemp()
#         self.source = io.StringIO(html)
#         self.file_name = 'index.html'
#         self.utx = urls.URLTransformer(self.url, self.url, self.path, self.file_name)
#
#         # self.reset()
#         self.w.set_source(self.source)
#         self.w.utx = self.utx
#
#     def tearDown(self):
#         # self.reset()
#         self.w = None
#         self.url = None
#         self.source = None
#         self.file_name = None
#         self.utx = None
#         if os.path.exists(self.path):
#             shutil.rmtree(self.path)
#         self.path = None
#
#     def test_utx(self):
#         self.assertEqual(self.utx, self.w.utx)
#         self.assertEqual(self.path, self.w.utx.base_path)
#
#     def test_parsing(self):
#         # self.reset()
#         # self.w.set_source(self.source)
#         # self.assertTrue(self.w.get_source())
#         # self.w.utx = self.utx
#         self.w.parse()
#         # self.assertTrue(self.w.elements)
#         # pprint(self.source.read())
#         # print(lxml.html.tostring(self.w.root))
#         # elements = sorted(self.w.elements, key=lambda x: x.__class__.__name__)
#         # print(elements)
#         self.assertEqual(len(self.w.elements), 7)
#
#         # def test_elements_properties(self):
#         # self.w.set_source(self.source)
#         # self.w.utx = self.utx
#         # self.w.parse()
#
#         # print(lxml.html.tostring(self.w.root))
#         for e in self.w.elements:
#             # print(e.file_path)
#             # print(self.path)
#             # print(self.w.utx.file_path)
#             # unique files must be stored
#             self.assertEqual(self.path, e.base_path)
#             self.assertEqual(self.url, e.base_url)
#             self.assertTrue(e.file_path.startswith(self.path))
#             # urls must be absolute
#             self.assertTrue(e.url.startswith('http'))
#             self.assertTrue(os.path.basename(e.file_path))
#
#     def test_crawler_sub_page(self):
#         self.w.parse()
#         for e in self.w.elements:
#             self.assertTrue(e.file_path.startswith(self.path))
