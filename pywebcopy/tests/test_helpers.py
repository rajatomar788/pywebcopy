# Copyright 2019; Raja Tomar
import unittest
from threading import Event

from six import BytesIO

from pywebcopy.helpers import CallbackFileWrapper


class TestCallbackFileWrapperWithBinary(unittest.TestCase):
    def setUp(self):
        self.fp = BytesIO(b'test')
        self.ans = CallbackFileWrapper(self.fp)

    def test_is_fp_closed_with_source_open(self):
        self.assertFalse(self.ans.closed)
        self.assertFalse(self.ans._CallbackFileWrapper__is_fp_closed())

    def test_is_fp_closed_with_source_closed(self):
        self.fp.close()
        self.assertTrue(self.ans.closed)
        self.assertTrue(self.ans._CallbackFileWrapper__is_fp_closed())

    def test_tell_position(self):
        self.ans.read()
        self.assertEqual(self.fp.tell(), self.ans.tell())

    def test_source_closed_flag(self):
        self.fp.close()
        self.assertTrue(self.ans.closed)

    def test_once_done_flag_before_close_call(self):
        self.assertFalse(self.ans._CallbackFileWrapper__once_done)

    def test_once_done_flag_after_close_call(self):
        self.ans.close()
        self.assertTrue(self.ans._CallbackFileWrapper__once_done)

    def test_callback_after_close_call(self):
        event = Event()
        self.ans._CallbackFileWrapper__callback = event.set
        self.assertFalse(event.is_set())
        self.ans.close()
        self.assertTrue(event.is_set())

    def test_read_method(self):
        self.assertEqual(self.fp.getvalue(), self.ans.read())

    def test_read_method_with_source_closed(self):
        self.fp.close()
        with self.assertRaises(ValueError):
            self.ans.read()

    def test_buffer_before_read_call(self):
        self.assertEqual(b'', self.ans._CallbackFileWrapper__buf.getvalue())

    def test_buffer_after_read_call(self):
        self.ans.read()
        self.assertEqual(
            self.fp.getvalue(),
            self.ans._CallbackFileWrapper__buf.getvalue())

    def test_rewind_method_before_once_done_flag(self):
        self.ans.rewind()
        self.assertEqual(self.fp, self.ans._CallbackFileWrapper__fp)

    def test_rewind_method_before_close_call(self):
        self.ans.rewind()
        self.assertEqual(self.fp, self.ans._CallbackFileWrapper__fp)

    def test_rewind_method_after_close_call(self):
        self.ans.close()
        self.assertTrue(self.ans.closed)
        buf = self.ans._CallbackFileWrapper__buf
        self.assertFalse(buf.closed)
        self.ans.rewind()
        self.assertEqual(buf, self.ans._CallbackFileWrapper__fp)
        self.assertFalse(self.ans.closed)

    def test_closed_flag_after_rewind_call(self):
        self.ans.close()
        self.assertTrue(self.ans.closed)
        self.ans.rewind()
        self.assertFalse(self.ans.closed)

    def test_read_method_after_rewind(self):
        data = self.ans.read()
        self.ans.close()
        self.ans.rewind()
        self.assertEqual(data, self.ans.read())


if __name__ == '__main__':
    unittest.main()
