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
        self.assertNotEqual(d['key2'], 'value2')
        self.assertEqual(d['key2'], 'value2changed')

    def test_deletion(self):

        d = structures.CaseInsensitiveDict()
        d['kEY2'] = 'value2'
        del d['key2']
        self.assertFalse('key2' in d)

    def test_iter(self):
        d = structures.CaseInsensitiveDict()
        d['kEY1'] = 'value1'
        d['kEY2'] = 'value2'
        d['kEY3'] = 'value3'
        self.assertListEqual(list(d), ['key1', 'key2', 'key3'])
        self.assertDictEqual(dict((('key1', 'value1'), ('key2', 'value2'), ('key3', 'value3'))), dict(d))
        self.assertListEqual(['value1', 'value2', 'value3'], list(d.values()))

    def test_len(self):
        d = structures.CaseInsensitiveDict()
        d['kEY1'] = 'value1'
        d['kEY2'] = 'value2'
        d['kEY3'] = 'value3'
        self.assertTrue(len(d) == 3)

    def test_copy(self):
        d = structures.CaseInsensitiveDict()
        d['kEY1'] = 'value1'
        d['kEY2'] = 'value2'
        d['kEY3'] = 'value3'
        self.assertDictEqual(dict(d), {'key1':'value1', 'key2':'value2', 'key3':'value3'})

    def test_equal(self):
        d = structures.CaseInsensitiveDict()
        d['kEY1'] = 'value1'
        d['kEY2'] = 'value2'
        d['kEY3'] = 'value3'
        self.assertTrue(dict(d) == {'key1':'value1', 'key2':'value2', 'key3':'value3'})

    def test_update(self):
        d = structures.CaseInsensitiveDict()
        d['kEY1'] = 'value1'
        d['kEY2'] = 'value2'
        d['kEY3'] = 'value3'
        d.update({'key3': 'changed'})
        self.assertTrue(d['key3'] == 'changed')


import pywebcopy.urls as pkg


class TestURLTranformer(unittest.TestCase):
    def test_url_parsing(self):
        obj = pkg.URLTransformer('http://some-site.com:80/path/#frag?query')
        obj.default_filename = 'index.html'
        obj._unique_fn_required = False
        self.assertEqual(obj.original_url, 'http://some-site.com:80/path/#frag?query')
        self.assertEqual(obj.url, 'http://some-site.com:80/path/#frag?query')
        self.assertEqual(obj.parsed_url, urlparse.urlsplit('http://some-site.com:80/path/',
                                                             allow_fragments=False))
        self.assertEqual(obj.parsed_url.port, 80)
        self.assertEqual(obj.hostname, 'some-site.com')
        self.assertEqual(obj.url_path, '/path/')
        self.assertEqual(obj.file_name, 'index.html')
        self.assertEqual(obj.to_path, url2pathname('some-site.com/path/'))
        self.assertEqual(obj.file_path, url2pathname('some-site.com/path/index.html'))

    def test_url_parsing_2(self):
        obj = pkg.URLTransformer('http://some-site.com:80')
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
        obj = pkg.URLTransformer('../some/rel/path/')
        obj.base_url = "http://some-site.com:80/"
        obj.base_path = "e:\\tests\\"
        obj.default_filename = 'index.html'
        obj._unique_fn_required = False

        self.assertEqual(obj.original_url, '../some/rel/path/')
        self.assertEqual(obj.url, 'http://some-site.com:80/some/rel/path/')
        self.assertEqual(obj.parsed_url, urlparse.urlsplit('http://some-site.com:80/some/rel/path/', allow_fragments=False))
        self.assertEqual(obj.parsed_url.port, 80)
        self.assertEqual(obj.hostname, 'some-site.com')
        self.assertEqual(obj.url_path, '/some/rel/path/')
        self.assertEqual(obj.file_name, 'index.html')
        self.assertEqual(obj.to_path, 'e:\\tests\\some-site.com\\some\\rel\\path\\')
        self.assertEqual(obj.file_path, url2pathname('e://tests/some-site.com/some/rel/path/index.html').lower())

    def test_file_detection(self):
        obj = pkg.URLTransformer('')

        self.assertEqual(obj.get_fileext_and_pos('/path/file.ext'), ('ext', 11))
        self.assertEqual(obj.get_fileext_and_pos('/path/file'), ('', 0))
        self.assertEqual(obj.get_fileext_and_pos('/path/file/'), ('', 0))
        self.assertEqual(obj.get_filename_and_pos('/path/file.ext'), ('file.ext', 6))
        self.assertEqual(obj.get_filename_and_pos('/path/file.ext'), ('file.ext', 6))

    def test_filename_refactoring(self):
        obj = pkg.URLTransformer("http://some-site.com/")
        obj.default_filename = 'index.html'
        obj.default_fileext = 'new'
        obj.check_fileext = True
        _base = '/path/' + str(obj.__hash__()) + '__'
        self.assertEqual(obj._refactor_filename('/path/file.ext'), (_base + 'file.new', 6))
        self.assertEqual(obj._refactor_filename('/path/file'), (_base + 'file.new', 6))
        self.assertEqual(obj._refactor_filename('/path/file/'), ( '/path/file/index.new', 11))

    def test_check_filename_generation(self):
        obj = pkg.URLTransformer('../path/file')   # path without extension
        obj.base_url = "http://some-site.com/"
        obj.base_path = "e:\\tests\\"
        obj.default_filename = 'index.html'
        obj.default_fileext = 'html'
        obj.check_fileext = True

        self.assertEqual(obj.file_name, 'file')
        self.assertEqual(obj.file_path, url2pathname('e://tests/some-site.com/path/'+str(hash(obj))+'__file.html').lower())

    def test_url_cleaning(self):
        obj = pkg.URLTransformer('')
        self.assertEqual(obj.clean_url('http://google.com/../../url/path/#frag'), 'http://google.com/url/path/')
        self.assertEqual(obj.clean_url('../../url/path'), 'url/path')
        self.assertEqual(obj.clean_url('./same/dir/'), 'same/dir/')


if __name__ == '__main__.py':
    unittest.main()
