# Copyright 2020; Raja Tomar
# See license for more details
import os.path
import hashlib
import unittest
import six

import pywebcopy.urls
from pywebcopy.urls import get_etag
from pywebcopy.urls import split_first
from pywebcopy.urls import common_prefix_map
from pywebcopy.urls import get_prefix
from pywebcopy.urls import common_suffix_map
from pywebcopy.urls import get_suffix
from pywebcopy.urls import get_content_type_from_headers
from pywebcopy.urls import Url
from pywebcopy.urls import parse_url
from pywebcopy.urls import get_host
from pywebcopy.urls import relate
from pywebcopy.urls import secure_filename


class TestBasicTools(unittest.TestCase):
    def test_get_etag_non_binary(self):
        data = 'data'
        self.assertEqual(hashlib.md5(data.encode()).hexdigest(), get_etag(data))

    def test_get_etag_binary(self):
        data = 'data'.encode()
        self.assertEqual(hashlib.md5(data).hexdigest(), get_etag(data))

    def test_split_first(self):
        self.assertEqual(split_first('path/?q=v#frag', '?#'), ('path/', 'q=v#frag', '?'))
        self.assertEqual(split_first('foo/bar?baz', '?/='), ('foo', 'bar?baz', '/'))
        self.assertEqual(split_first('foo/bar?baz', '123'), ('foo/bar?baz', '', None))

    def test_get_prefix(self):
        prefix = common_prefix_map.get('text/html')
        self.assertEqual(prefix, get_prefix('text/html'))

    def test_get_suffix(self):
        suffix = common_suffix_map.get('image/x-icon')
        self.assertEqual(suffix, '.ico')
        self.assertEqual(suffix, get_suffix('image/x-icon'))

    def test_get_content_type_from_headers(self):
        self.assertEqual('text/html', get_content_type_from_headers({'Content-Type': 'text/html'}))
        self.assertEqual('text/html', get_content_type_from_headers({'Content-Type': 'text/html; charset=utf-8'}))
        self.assertEqual(None, get_content_type_from_headers({}, default=None))
        self.assertEqual('text/html', get_content_type_from_headers({}, default='text/html'))

    def test_parse_url(self):
        # This functionality is copied from urllib3 so it shouldn't require rigorous testing.
        self.assertEqual(parse_url('http://google.com/mail/'),
                         Url(scheme='http', auth=None, host='google.com', port=None, path='/mail/',
                             query=None, fragment=None))
        self.assertEqual(parse_url('google.com:80'),
                         Url(scheme=None, auth=None, host='google.com', port=80, path=None,
                             query=None, fragment=None))
        self.assertEqual(parse_url('/foo?bar'), Url(scheme=None, auth=None, host=None, port=None, path='/foo',
                                                    query='bar', fragment=None))
        self.assertEqual(parse_url('/foo?bar#baz'), Url(scheme=None, auth=None, host=None, port=None, path='/foo',
                                                        query='bar', fragment='baz'))
        self.assertEqual(parse_url('https://username:password@google.com:443/mail/'),
                         Url(scheme='https', auth='username:password', host='google.com', port=443, path='/mail/',
                             query=None, fragment=None))

    def test_get_host(self):
        self.assertEqual(get_host('http://google.com:80/path'), ('http', 'google.com', 80))
        self.assertEqual(get_host('https://google.com/path'), ('https', 'google.com', None))
        self.assertEqual(get_host('google.com:80/path'), ('http', 'google.com', 80))

    def test_URL(self):
        self.assertEqual(Url(scheme=None, auth=None, host='google.com', port=80, path=None,
                             query=None, fragment=None).netloc, 'google.com:80')
        self.assertEqual(Url(scheme='http', auth=None, host='google.com', port=None, path='/mail/',
                             query=None, fragment=None).hostname, 'google.com')
        self.assertEqual(Url(scheme=None, auth=None, host='google.com', port=80, path=None,
                             query=None, fragment=None).netloc, 'google.com:80')
        self.assertEqual(Url(scheme=None, auth=None, host=None, port=None, path='/foo',
                             query='bar', fragment=None).netloc, None)
        self.assertEqual(Url(scheme=None, auth=None, host=None, port=None, path='/foo',
                             query='bar', fragment='baz').request_uri, '/foo?bar')
        self.assertEqual(Url(scheme='https', auth='username:password', host='google.com', port=443, path='/mail/',
                             query=None, fragment=None).url, 'https://username:password@google.com:443/mail/')

    def test_relate(self):
        self.assertEqual(relate('css/style.css', 'index.html'), os.path.normpath('css/style.css'))
        self.assertEqual(relate('css/style.css', 'html/index.html'), os.path.normpath('../css/style.css'))
        self.assertEqual(relate('css/style.css', 'html'), os.path.normpath('css/style.css'))
        self.assertEqual(relate('css/style.css', 'html/'), os.path.normpath('../css/style.css'))


class TestUrl2Path(unittest.TestCase):
    def test_filter_and_group_url_with_stem(self):
        s = 'http://www.nx-domain.com/blog/index?q=query#fragment'
        self.assertEqual(pywebcopy.urls._filter_and_group_segments(s, remove_query=True, remove_frag=True),
                         (('www.nx-domain.com', 'blog'), 'index', ''))
        self.assertEqual(pywebcopy.urls._filter_and_group_segments(s, remove_query=False, remove_frag=True),
                         (('www.nx-domain.com', 'blog'), 'index_q_query', ''))
        self.assertEqual(pywebcopy.urls._filter_and_group_segments(s, remove_query=False, remove_frag=False),
                         (('www.nx-domain.com', 'blog'), 'index_q_query_fragment', ''))

    def test_filter_and_group_url_without_stem(self):
        s = 'http://www.nx-domain.com/blog/?q=query#fragment'
        self.assertEqual(pywebcopy.urls._filter_and_group_segments(s, remove_query=True, remove_frag=True),
                         (('www.nx-domain.com', 'blog'), '', ''))
        self.assertEqual(pywebcopy.urls._filter_and_group_segments(s, remove_query=False, remove_frag=True),
                         (('www.nx-domain.com', 'blog'), 'q_query', ''))
        self.assertEqual(pywebcopy.urls._filter_and_group_segments(s, remove_query=False, remove_frag=False),
                         (('www.nx-domain.com', 'blog'), 'q_query_fragment', ''))

    def test_coerce_args_with_non_consistent_types(self):
        with self.assertRaises(TypeError):
            pywebcopy.urls._coerce_args(b'a', u'b')

    def test_coerce_args_of_text_type(self):
        a, b, enc = pywebcopy.urls._coerce_args(u'a', None)
        self.assertTrue(isinstance(a, six.string_types))
        self.assertTrue(b is None)
        self.assertEqual(enc(a), a)
        self.assertEqual(enc(b), b)

    def test_coerce_args_of_binary_type(self):
        a, b, enc = pywebcopy.urls._coerce_args(b'a', None)
        self.assertTrue(isinstance(a, six.string_types))
        self.assertEqual(b, u'')
        self.assertEqual(enc(a), b'a')
        self.assertEqual(enc(b), b'')

    def test_secure_filename(self):
        for i in ['!', '~', '`', '#', '@', '$', '%', '^', '&', '*', '(', ')',
                  '+', '|', '?', '[', ']', ':', ';', ',', '.']:
            with self.subTest(i=i):
                self.assertEqual(secure_filename(i), '')
        self.assertEqual(secure_filename('http://localhost:5000'), 'http__localhost_5000')
        self.assertEqual(secure_filename('http://localhost/../some/deformity'), 'http__localhost_.._some_deformity')
        self.assertEqual(secure_filename('http://localhost:5000/?path#frag'), 'http__localhost_5000__path_frag')
        self.assertEqual(secure_filename('http://localhost:5000?q=search'), 'http__localhost_5000_q_search')
        self.assertEqual(secure_filename('..//..\\..path'), 'path')
        for i in ["NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8",
                  "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]:

            if os.name == 'nt':
                self.assertEqual(secure_filename(i), '_' + i)
            else:
                self.assertEqual(secure_filename(i), i)
