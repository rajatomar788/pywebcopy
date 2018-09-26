import unittest
import pywebcopy.core as pkg


class TestCore(unittest.TestCase):
    def test_get(self):
        self.assertEqual(pkg.get('htpsasdkfklsdfkjsdf'), None)


if __name__ == '__main__':
    unittest.main()