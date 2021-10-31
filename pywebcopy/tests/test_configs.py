# Copyright 2019; Raja Tomar
import os
import tempfile
import unittest

from pywebcopy import configs
from pywebcopy.urls import Context
from pywebcopy.session import Session
from pywebcopy.core import WebPage
from pywebcopy.schedulers import Scheduler


class TestConfigs(unittest.TestCase):

    def test_session_creation(self):
        ans = configs.get_config('http://localhost:5000')
        ans.__setitem__('bypass_robots', True)
        ans.__setitem__('http_cache', True)
        ans.__setitem__('delay', 1)
        ans.__setitem__('http_headers', {'User-Agent': 'test-bot'})
        sess = ans.create_session()
        self.assertTrue(isinstance(sess, Session))
        self.assertEqual(sess.follow_robots_txt, False)
        from cachecontrol import CacheControlAdapter
        for i in sess.adapters.values():
            self.assertTrue(isinstance(i, CacheControlAdapter))
        self.assertEqual(sess.delay, 1)
        self.assertEqual(sess.headers, {'User-Agent': 'test-bot'})

    def test_context_creation(self):
        ans = configs.get_config('http://localhost:5000')
        ans.__setitem__('tree_type', 'HIERARCHY')
        context = ans.create_context()
        self.assertTrue(isinstance(context, Context))
        self.assertEqual(context.tree_type, 'HIERARCHY')

    def test_simple_page_creation(self):
        ans = configs.get_config('http://localhost:5000')
        page = ans.create_page()
        self.assertTrue(isinstance(page, WebPage))
        self.assertTrue(isinstance(page.session, Session))
        self.assertTrue(isinstance(page.context, Context))
        self.assertTrue(isinstance(page.scheduler, Scheduler))
        self.assertEqual(page.session.follow_robots_txt, not ans.get('bypass_robots'))
        self.assertEqual(page.session.delay, ans.get('delay'))
        self.assertEqual(page.session.headers,
                         configs.default_headers(**configs.safe_http_headers))


class TestGetConfigFactory(unittest.TestCase):
    def test_simple(self):
        ans = configs.get_config('http://localhost:5000')
        self.assertTrue(isinstance(ans, configs.ConfigHandler))
        self.assertEqual(ans.get('project_url'), 'http://localhost:5000')
        self.assertEqual(ans.get('project_name'), 'http_localhost_5000')
        self.assertEqual(ans.get('project_folder'),
                         os.path.join(tempfile.gettempdir(), ans.get('project_name')))
        for k, v in configs.default_config.items():
            if k in ('project_url', 'project_name', 'project_folder'):
                continue
            self.assertEqual(ans.get(k), v)

    def test_all_arguments(self):
        ans = configs.get_config('http://localhost:5000', project_folder='home/user/', project_name='my_project',
                                 bypass_robots=True, delay=1)
        self.assertTrue(isinstance(ans, configs.ConfigHandler))
        self.assertEqual(ans.get('project_url'), 'http://localhost:5000')
        self.assertEqual(ans.get('project_name'), 'my_project')
        self.assertEqual(ans.get('project_folder'), os.path.join(os.path.abspath('home/user/'),
                                                                 ans.get('project_name')))
        self.assertEqual(ans.get('bypass_robots'), True)
        self.assertEqual(ans.get('delay'), 1)
        os.removedirs(ans.get('project_folder'))
