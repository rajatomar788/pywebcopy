import os
import unittest
from pywebcopy.configs import default_config
from pywebcopy.configs import ConfigHandler


class TestConfig(unittest.TestCase):
    def test_setup_paths(self):
        d = ConfigHandler(default_config)
        d.setup_paths('e://tests//', 'Test')
        self.assertTrue(os.path.isdir('e://tests//'))
        self.assertTrue(os.path.isdir(d['project_folder']))
        self.assertTrue(os.path.isfile(d['log_file']))
        self.assertTrue(d['project_name'] == 'Test')
        self.assertTrue(d['project_folder'].endswith('Test'))

    def test_reset(self):
        d = ConfigHandler(default_config)
        d.setup_paths('e://tests//', 'Test')
        self.assertNotEqual(d, default_config)
        d.reset_config()
        self.assertEqual(d, default_config)

def main():
    unittest.main()


if __name__ == '__main__.py':
    main()
