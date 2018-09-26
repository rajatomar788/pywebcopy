import unittest
from pywebcopy.config import ConfigHandler as pkg


class TestConfig(unittest.TestCase):
    def test_new_item(self):
        d = pkg()
        d['KeY'] = 'value'
        d['kEY2'] = 'value2'
        d['Key2'] = 'value2changed'

        d.attr = 'value'
        d.attr2 = 'value2'

        d.attr2 = 'value2changed'

        self.assertEqual(d['key'], 'value')
        self.assertEqual(d['key2'], 'value2changed')

        self.assertEqual(d.attr, 'value')

        self.assertEqual(d.attr2, 'value2changed')


def main():
    unittest.main()


if __name__ == '__main__':
    main()
