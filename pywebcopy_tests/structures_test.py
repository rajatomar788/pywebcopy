import unittest

try:
    import urlparse
    from urllib import url2pathname
except ImportError:
    from urllib import parse as urlparse
    from urllib.request import url2pathname as url2pathname

import pywebcopy.structures as structures


class TestCaseInsensitiveDict(unittest.TestCase):
    def test_new_item(self):

        d = structures.CaseInsensitiveDict()
        d['KeY'] = 'value'
        d['kEY2'] = 'value2'
        d['Key2'] = 'value2changed'

        self.assertEqual(d['key'], 'value')
        self.assertEqual(d['key2'], 'value2changed')


import pywebcopy.urls as pkg


class TestUrl(unittest.TestCase):
    def test_url_parsing(self):
        obj = pkg.Url('http://some-site.com:80/path/#frag?query')
        obj.default_filename = 'index.html'
        obj._unique_fn_required = False
        self.assertEqual(obj.original_url, 'http://some-site.com:80/path/#frag?query')
        self.assertEqual(obj.url, 'http://some-site.com:80/path/#frag?query')
        self.assertEqual(obj.parsed_url, urlparse.urlsplit('http://some-site.com:80/path/#frag?query',
                                                             allow_fragments=False))
        self.assertEqual(obj.parsed_url.port, 80)
        self.assertEqual(obj.hostname, 'some-site.com')
        self.assertEqual(obj.url_path, '/path/')
        self.assertEqual(obj.file_name, 'index.html')
        self.assertEqual(obj.to_path, url2pathname('some-site.com/path/'))
        self.assertEqual(obj.file_path, url2pathname('some-site.com/path/index.html'))

    def test_url_parsing_2(self):
        obj = pkg.Url('http://some-site.com:80')
        obj.default_filename = 'index.html'
        obj._unique_fn_required = False
        self.assertEqual(obj.original_url, 'http://some-site.com:80')
        self.assertEqual(obj.url, 'http://some-site.com:80')
        self.assertEqual(obj.parsed_url, urlparse.urlsplit('http://some-site.com:80',
                                                             allow_fragments=False))
        self.assertEqual(obj.parsed_url.port, 80)
        self.assertEqual(obj.hostname, 'some-site.com')
        self.assertEqual(obj.url_path, '')
        self.assertEqual(obj.file_name, 'index.html')
        self.assertEqual(obj.to_path, url2pathname('some-site.com'))
        self.assertEqual(obj.file_path, url2pathname('some-site.com/index.html'))

    def test_url_parsing_after_set_base(self):
        obj = pkg.Url('../some/rel/path/')
        obj.base_url = "http://some-site.com:80"
        obj.base_path = "e:\\tests\\"
        obj.default_filename = 'index.html'
        obj._unique_fn_required = False
        self.assertEqual(obj.original_url, '../some/rel/path/')
        self.assertEqual(obj.url, 'http://some-site.com:80/some/rel/path/')
        self.assertEqual(obj.parsed_url, urlparse.urlsplit('http://some-site.com:80/some/rel/path/',
                                                             allow_fragments=False))
        self.assertEqual(obj.parsed_url.port, 80)
        self.assertEqual(obj.hostname, 'some-site.com')
        self.assertEqual(obj.url_path, '/some/rel/path/')
        self.assertEqual(obj.file_name, 'index.html')
        self.assertEqual(obj.to_path, 'e:\\tests\\some-site.com\\some\\rel\\path\\')
        self.assertEqual(obj.file_path, url2pathname('e://tests/some-site.com/some/rel/path/index.html').lower())


if __name__ == '__main__':
    unittest.main()
