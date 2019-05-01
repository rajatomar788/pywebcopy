import os.path
import unittest
import pywebcopy.core as core


class TestCore(unittest.TestCase):
    def test_get(self):
        self.assertEqual(core.get('htpsasdkfklsdfkjsdf'), None)

    def test_can_access(self):
        # Note that the robots parser is not set yet
        # NOTE: the object is subclass of robotfileparser of standard library
        # thus it is already well tested
        self.assertEqual(core._can_access('/url/'), True)

    def test_file_writing(self):
        loc = 'e://tests/'
        content = b'Sample content'
        saved = core.new_file(loc, content=content)
        self.assertEqual(loc, saved, "File path does not match.")
        self.assertTrue(os.path.exists(saved), "File didn't get saved.")


if __name__ == '__main__':
    unittest.main()