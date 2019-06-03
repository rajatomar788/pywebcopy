import io
import os
import shutil
import tempfile
import unittest

import pywebcopy.configs
import pywebcopy.structures
import pywebcopy.urls
import pywebcopy.elements
from pywebcopy.compat import urlsplit, url2pathname, urlparse, urljoin


class TestCaseInsensitiveDict(unittest.TestCase):

    @staticmethod
    def _new_object():
        return pywebcopy.structures.CaseInsensitiveDict()

    def test_set_item(self):
        d = self._new_object()

        d['KeY'] = 'value'
        d['kEY2'] = 'value2'
        self.assertEqual(d['key'], 'value')
        self.assertEqual(d['key2'], 'value2')

        d['Key2'] = 'value2changed'
        self.assertEqual(d['key2'], 'value2changed')

    def test_get_item(self):
        d = self._new_object()
        d['KeY'] = 'value'
        d['kEY2'] = 'value2'
        d['key3'] = 'value3'
        d['key4'] = 'value4'
        d['key5'] = 'value5'
        self.assertEqual(d['key'], 'value')
        self.assertEqual(d['key2'], 'value2')
        self.assertEqual(d['key3'], 'value3')
        self.assertEqual(d['key4'], 'value4')
        self.assertEqual(d['key5'], 'value5')
        self.assertTrue('key' in d)
        self.assertTrue('key2' in d)
        self.assertTrue('key3' in d)
        self.assertTrue('key4' in d)
        self.assertTrue('key5' in d)
        with self.assertRaises(KeyError):
            d.pop('key6')

    def test_del(self):
        d = self._new_object()
        d['key'] = 'value'
        self.assertEqual(d['key'], 'value')
        del d['key']
        self.assertEqual(d.get('key', None), None)

    def test_iter(self):
        d = self._new_object()
        d['KeY'] = 'value'
        d['kEY2'] = 'value2'
        should_be = {'key': 'value', 'key2': 'value2'}

        self.assertEqual(d, should_be)

        for k, v in d.items():
            self.assertTrue(should_be[k] == v)


class TestConfigHandlerBasic(unittest.TestCase):

    def setUp(self):
        self.c = pywebcopy.configs.ConfigHandler()

    def tearDown(self):
        self.c = None

    def test_reset_config(self):
        self.c.update({'key': 'value', 'key2': 'value2'})
        self.assertEqual(dict(self.c), {'key': 'value', 'key2': 'value2'})
        self.c.reset_config()
        self.assertTrue('key' not in self.c)
        self.assertTrue('key2' not in self.c)
        self.assertEqual(dict(self.c), {})

        with self.assertRaises(KeyError):
            self.c.pop('key')
            self.c.pop('key2')

    def test_reset_key(self):
        d = {'key': 'value', 'key2': 'value2'}
        self.c.update(d)
        self.c.reset_key('key')
        self.assertNotEqual(d['key'], self.c.get('key'))
        self.assertEqual(None, self.c.get('key'))

    def test_is_set_check_before(self):
        self.assertEqual(dict(self.c), {})
        self.assertFalse(self.c.is_set())

    def test_is_set_check_after(self):
        self.c.update({'project_name': 'v', 'project_folder': 'v2', 'log_file': 'v3'})
        self.assertNotEqual(dict(self.c), {})
        self.assertTrue(self.c.is_set())
        self.c.reset_config()


class TestConfigHandler(unittest.TestCase):

    def setUp(self):
        self.c = pywebcopy.configs.ConfigHandler()
        self.path = tempfile.mkdtemp()
        self.name = 'test'

    def tearDown(self):
        self.c = None
        if os.path.exists(self.path):
            try:
                shutil.rmtree(self.path)
            except PermissionError:
                pass
        self.path = None
        self.name = None

    def test_setup_paths(self):
        self.c.setup_paths(self.path, self.name)
        self.assertEqual(self.name, self.c.get('project_name'))
        self.assertEqual(os.path.join(self.path, self.name), self.c.get('project_folder'))

    def test_setup_paths_bad_data(self):
        with self.assertRaises(TypeError):
            self.c.setup_paths(int, None)


class TestUrlMethods(unittest.TestCase):

    def setUp(self):
        self.p = pywebcopy.urls.URLTransformer('')

    def tearDown(self):
        self.p = None

    def test_get_filename_and_pos(self):
        self.assertEqual(self.p.get_filename_and_pos('/home/file.ext'), ('file.ext', 6))

    def test_get_filename_and_pos2(self):
        self.assertEqual(self.p.get_filename_and_pos('/home///file.ext'), ('file.ext', 8))

    def test_get_filename_and_pos3(self):
        self.assertEqual(self.p.get_filename_and_pos('/home/file'), ('file', 6))

    def test_get_filename_and_pos4(self):
        self.assertEqual(self.p.get_filename_and_pos('/home/file/'), ('', 11))

    def test_get_fileext_and_pos(self):
        self.assertEqual(self.p.get_fileext_and_pos('/home/file.ext'), ('ext', 11))

    def test_get_fileext_and_pos2(self):
        self.assertEqual(self.p.get_fileext_and_pos('/home///file.ext'), ('ext', 13))

    def test_get_fileext_and_pos3(self):
        self.assertEqual(self.p.get_fileext_and_pos('/home/file'), ('', 0))

    def test_get_fileext_and_pos4(self):
        self.assertEqual(self.p.get_fileext_and_pos('/home/file/'), ('', 0))

    def test_refactor_filename(self):
        self.assertEqual(self.p._refactor_filename('/home/file.ext'),
                         ('/home/' + self.p._hex() + '__file.ext', 6))

    def test_refactor_filename2(self):
        self.assertEqual(self.p._refactor_filename('/home///file.ext'),
                         ('/home///' + self.p._hex() + '__file.ext', 8))

    def test_refactor_filename3(self):
        self.assertEqual(self.p._refactor_filename('/home/file'),
                         ('/home/' + self.p._hex() + '__file.' + self.p.default_suffix, 6))

    def test_refactor_filename4(self):
        self.assertEqual(self.p._refactor_filename('/home/file/'),
                         ('/home/file/' + self.p.default_filename, 11))

    def test_clean_url(self):
        self.assertEqual(self.p.clean_url('http://google.com/../../url/path/#frag'),
                         'http://google.com/url/path/')

    def test_clean_url2(self):
        self.assertEqual(self.p.clean_url('../../url/path'), 'url/path')

    def test_clean_url3(self):
        self.assertEqual(self.p.clean_url('./same/dir/'), 'same/dir/')

    def test_clean_url4(self):
        self.assertEqual(self.p.clean_url('.././url/path'), 'url/path')

    def test_clean_url5(self):
        self.assertEqual(self.p.clean_url('./same/dir/../'), 'same/dir/')

    def test_clean_fn(self):
        pass


class TestUrl2(unittest.TestCase):

    def setUp(self):
        self.url = 'http://some-site.com:80'
        self.file_name = 'index.html'
        self.utx = pywebcopy.urls.URLTransformer(self.url, default_fn=self.file_name)

    def tearDown(self):
        self.url = None
        self.file_name = None
        self.utx = None

    def test_utx_url(self):
        self.assertEqual(self.url, self.utx.url)

    def test_utx_base_url(self):
        self.assertEqual(None, self.utx.base_url)

    def test_utx_base_path(self):
        self.assertEqual(None, self.utx.base_path)

    def test_utx_file_name(self):
        self.assertEqual(self.file_name, self.utx.file_name)

    def test_utx_file_path(self):
        self.assertEqual(
            os.path.join(urlparse(self.url).hostname, self.file_name),
            self.utx.file_path
        )

    def test_url_parsing_2(self):
        # obj._unique_fn_required = False
        self.assertEqual(self.utx._url, 'http://some-site.com:80')
        self.assertEqual(self.utx.url, 'http://some-site.com:80')
        self.assertEqual(self.utx.parsed_url, urlsplit('http://some-site.com:80'))
        self.assertEqual(self.utx.parsed_url.port, 80)
        self.assertEqual(self.utx.hostname, 'some-site.com')
        self.assertEqual(self.utx.url_path, '')
        # self.assertEqual(self.utx.file_name, 'index.html')
        self.assertEqual(self.utx.to_path, url2pathname('some-site.com'))
        self.assertEqual(self.utx.file_path, url2pathname('some-site.com/index.html'))

    def test_url_parsing(self):
        obj = pywebcopy.urls.URLTransformer('http://some-site.com:80/path/#frag?query')
        obj.default_filename = 'index.html'
        # obj._unique_fn_required = False
        self.assertEqual(obj._url, 'http://some-site.com:80/path/#frag?query')
        self.assertEqual(obj.url, 'http://some-site.com:80/path/#frag?query')
        self.assertEqual(obj.parsed_url, urlsplit('http://some-site.com:80/path/'))
        self.assertEqual(obj.parsed_url.port, 80)
        self.assertEqual(obj.hostname, 'some-site.com')
        self.assertEqual(obj.url_path, '/path/')
        self.assertEqual(obj.file_name, 'index.html')
        self.assertEqual(obj.to_path, url2pathname('some-site.com/path'))
        self.assertEqual(obj.file_path, url2pathname('some-site.com/path/index.html'))


class TestUrl3(unittest.TestCase):

    def setUp(self):
        self.url = '../some/rel/path/'
        self.base_url = "http://some-site.com:80"
        self.path = tempfile.mkdtemp()
        self.file_name = 'index.html'
        self.utx = pywebcopy.urls.URLTransformer(self.url, self.base_url, self.path, self.file_name)

    def tearDown(self):
        self.url = None
        self.base_url = None
        self.file_name = None
        self.utx = None
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        self.path = None

    def test_utx_url(self):
        self.assertEqual(urljoin(self.base_url, self.url), self.utx.url)

    def test_url_split(self):
        self.assertEqual(urlsplit(urljoin(self.base_url, self.url)), self.utx.parsed_url)

    def test_utx_base_url(self):
        self.assertEqual(self.base_url, self.utx.base_url)

    def test_utx_base_path(self):
        self.assertEqual(self.path, self.utx.base_path)

    def test_utx_file_name(self):
        self.assertEqual(self.file_name, self.utx.file_name)

    def test_url_path(self):
        self.assertEqual(urlparse(urljoin(self.base_url, self.url)).path, self.utx.url_path)

    def test_to_path(self):
        pass

    def test_utx_file_path(self):
        self.assertEqual(
            os.path.join(self.utx.to_path, self.file_name),
            self.utx.file_path
        )

    def test_utx_to_path(self):
        self.assertEqual(
            self.utx.to_path,
            os.path.normpath(os.path.join(self.path, self.utx.hostname + self.utx.url_path))
        )


class TestUrlBadData(unittest.TestCase):

    # noinspection PyTypeChecker
    def setUp(self):
        self.url = 'http://some-site.com:80'
        self.file_name = 'index.html'
        self.utx = pywebcopy.urls.URLTransformer(self.url, default_fn=self.file_name)

    def tearDown(self):
        self.url = None
        self.file_name = None
        self.utx = None

    # noinspection PyTypeChecker
    def test_utx_url(self):
        with self.assertRaises(TypeError):
            pywebcopy.urls.URLTransformer(None)

    def test_none_type_base_url(self):
        with self.assertRaises(TypeError):
            self.utx.base_url = None

    def test_none_type_base_path(self):
        with self.assertRaises(TypeError):
            self.utx.base_path = None

    def test_utx_file_name(self):
        self.assertEqual(self.file_name, self.utx.file_name)

    def test_utx_file_path(self):
        self.assertEqual(
            os.path.join(urlparse(self.url).hostname, self.file_name),
            self.utx.file_path
        )


class TestUrlRealUseCase(unittest.TestCase):

    def setUp(self):
        self.url = 'http://test-site.com'
        self.path = tempfile.mkdtemp()
        self.file_name = 'index.html'
        self.utx = pywebcopy.urls.URLTransformer(self.url, self.url, self.path, self.file_name)

    def tearDown(self):
        self.url = None
        self.file_name = None
        self.utx = None
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        self.path = None

    def test_utx_url(self):
        self.assertEqual(self.url, self.utx.url)

    def test_utx_base_url(self):
        self.assertEqual(self.url, self.utx.base_url)

    def test_utx_base_path(self):
        self.assertEqual(self.path, self.utx.base_path)

    def test_utx_file_name(self):
        self.assertEqual(self.file_name, self.utx.file_name)

    def test_utx_relative_to(self):
        target = os.path.dirname(self.utx.file_path)
        start = os.path.dirname(self.path)
        rel_path = os.path.join(os.path.relpath(target, start), os.path.basename(self.utx.file_path))
        self.assertEqual(rel_path, self.utx.relative_to(self.path))

    def test_utx_file_path(self):
        self.assertEqual(
            os.path.join(self.path, urlparse(self.url).hostname, self.file_name),
            self.utx.file_path
        )


class TestFileMixin(unittest.TestCase):

    def setUp(self):
        self.url = 'http://test-site.com'
        self.path = tempfile.mkdtemp()
        self.file_name = 'index.html'
        self.data = b'test'
        self.utx = pywebcopy.elements.FileMixin(self.url, self.url, self.path, self.file_name)

    def tearDown(self):
        self.url = None
        self.file_name = None
        self.utx = None
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        self.path = None

    def test_file_path(self):
        self.assertEqual(
            os.path.join(self.path, urlparse(self.url).hostname, self.file_name),
            self.utx.file_path
        )

    def test_write_file_file_path(self):
        self.utx.write_file(io.BytesIO(self.data))
        self.assertTrue(os.path.exists(self.utx.file_path))

    def test_write_file_file_data(self):
        self.utx.write_file(io.BytesIO(self.data))
        with open(self.utx.file_path, 'rb') as f:
            d = f.read()
        self.assertEqual(self.data, d)


if __name__ == '__main__':
    unittest.main()
