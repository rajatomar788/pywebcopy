import unittest
import pywebcopy.parsers as pkg
import pywebcopy.exceptions as exc


class TestParser(unittest.TestCase):

    def test_urls_and_paths(self):
        try:
            p = pkg.parse('http://google.com')
            self.assertEqual(p.original_url, 'http://google.com')
            self.assertEqual(200, p.http_request.status_code)
            self.assertEqual(p.download_loc(), 'E:\\tests\\www.google.com\\index.html')
        except exc.ConnectionError:
            pass


def main():
    unittest.main()


if __name__ == '__main__':
    main()
