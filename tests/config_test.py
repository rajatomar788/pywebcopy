import unittest
from pywebcopy.configs import ConfigHandler as handler


class TestConfig(unittest.TestCase):
    def test_new_item(self):
        d = handler()
        d['KeY'] = 'value'
        d['kEY2'] = 'value2'
        d['Key2'] = 'value2changed'
        self.assertEqual(d['key'], 'value')
        self.assertEqual(d['key2'], 'value2changed')

        d.attr = 'value'
        d.attr2 = 'value2'
        d.attr2 = 'value2changed'
        self.assertEqual(d.attr, 'value')
        self.assertEqual(d.attr2, 'value2changed')

    def test_del(self):
        d = handler()
        d['key'] = 'value'
        self.assertEqual(d['key'], 'value')
        del d['key']
        self.assertEqual(d.get('key', None), None)

    def test_iter(self):
        d = handler()
        d['KeY'] = 'value'
        d['kEY2'] = 'value2'
        should_be = {'key': 'value', 'key2': 'value2'}
        self.assertEqual(d, should_be)
        for k, v in d.items():
            self.assertTrue(should_be[k] == v)

    def test_lookup(self):
        d = handler()
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

    def test_reset(self):
        d = handler()
        d['KeY'] = 'value'
        d['kEY2'] = 'value2'

        self.assertEqual(dict(d), {'key': 'value', 'key2': 'value2'})
        d.reset_config()
        self.assertTrue('key' not in d)
        self.assertTrue('key2' not in d)
        with self.assertRaises(KeyError):
            d.pop('key')
            d.pop('key2')


def main():
    unittest.main()


if __name__ == '__main__':
    main()
