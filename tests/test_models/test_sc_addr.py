import unittest

from sc_client import ScAddr
from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError


class TestScAddr(unittest.TestCase):
    def test_init(self):
        self.assertEqual(ScAddr().value, 0)
        self.assertEqual(ScAddr(0).value, 0)
        self.assertEqual(ScAddr(1).value, 1)
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.INT_TYPE_INITIALIZATION):
            # noinspection PyTypeChecker
            ScAddr("not int")

    def test_valid(self):
        self.assertFalse(ScAddr().is_valid())
        self.assertFalse(bool(ScAddr()))
        self.assertFalse(ScAddr(0).is_valid())
        self.assertFalse(bool(ScAddr(0)))
        self.assertTrue(ScAddr(1).is_valid())
        self.assertTrue(bool(ScAddr(1)))

    def test_equal(self):
        self.assertTrue(ScAddr().is_equal(ScAddr()))
        self.assertEqual(ScAddr(), ScAddr())
        self.assertTrue(ScAddr(1).is_equal(ScAddr(1)))
        self.assertEqual(ScAddr(1), ScAddr(1))
        addr = ScAddr(2)
        self.assertTrue(addr.is_equal(addr))
        self.assertEqual(addr, addr)
        self.assertFalse(ScAddr(1).is_equal(ScAddr(2)))
        self.assertNotEqual(ScAddr(1), ScAddr(2))
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR):
            # noinspection PyTypeChecker
            ScAddr(1).is_equal(1)

    def test_hash(self):
        self.assertEqual(hash(ScAddr(1)), hash(ScAddr(1)))
        self.assertNotEqual(hash(ScAddr(0)), hash(ScAddr(1)))
        self.assertNotEqual(hash(ScAddr(3)), hash(3))

    def test_lt(self):
        self.assertLess(ScAddr(1), ScAddr(2))
        self.assertGreater(ScAddr(3), ScAddr(2))
        self.assertEqual(sorted([ScAddr(2), ScAddr(3), ScAddr(1)]), [ScAddr(1), ScAddr(2), ScAddr(3)])

    def test_rshift(self):
        self.assertEqual(ScAddr(1) >> "alias", (ScAddr(1), "alias"))

    def test_repr(self):
        self.assertEqual(repr(ScAddr(123)), "ScAddr(123)")
