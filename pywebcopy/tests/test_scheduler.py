# Copyright 2019; Raja Tomar
import unittest

from requests import Response

from pywebcopy.schedulers import Index
from pywebcopy.schedulers import Scheduler
from pywebcopy.configs import get_config
from pywebcopy.elements import VoidResource


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.config = get_config('http://localhost:5000', debug=False)
        self.context = self.config.create_context()
        self.session = self.config.create_session()
        self.scheduler = Scheduler()
        self.resource = VoidResource(self.session, self.config, self.scheduler, self.context)
        self.response = Response()
        self.response.url = 'http://localhost:5000/'    # this url has '/' at the end
        self.response.encoding = 'utf-8'

    def tearDown(self):
        del self.config, self.context, self.session, self.scheduler, self.resource, self.response

    def test_add_entry(self):
        ans = Index()
        ans.add_entry('http://localhost:5000', 'http_localhost_5000//index.html')
        self.assertEqual(ans.get('http://localhost:5000'), 'http_localhost_5000//index.html')

    def test_get_entry(self):
        ans = Index()
        ans.add_entry('http://localhost:5000', 'http_localhost_5000//index.html')
        self.assertEqual(ans.get_entry('http://localhost:5000'), 'http_localhost_5000//index.html')
        ans.pop('http://localhost:5000')
        self.assertEqual(ans.get_entry('http://localhost:5000', None), None)

    def test_add_resource_without_response(self):
        ans = Index()
        ans.add_resource(self.resource)
        self.assertEqual(ans.get(self.resource.url), self.context.resolve())

    def test_add_resource_with_response(self):
        ans = Index()
        self.resource.response = self.response
        ans.add_resource(self.resource)
        self.assertEqual(ans.get(self.resource.url), self.context.resolve())
        self.assertEqual(ans.get(self.response.url), self.context.resolve())

    def test_add_resource_with_redirects(self):
        ans = Index()
        rdr1 = Response()
        rdr1.url = 'http://localhost:5000/redirect1'
        rdr2 = Response()
        rdr2.url = 'http://localhost:5000/redirect2'
        self.response.history.append(rdr1)
        self.response.history.append(rdr2)
        self.resource.response = self.response
        ans.add_resource(self.resource)
        self.assertEqual(ans.get(self.resource.url), self.context.resolve())
        self.assertEqual(ans.get(self.response.url), self.context.resolve())
        self.assertEqual(ans.get(rdr1.url), self.context.resolve())
        self.assertEqual(ans.get(rdr2.url), self.context.resolve())
