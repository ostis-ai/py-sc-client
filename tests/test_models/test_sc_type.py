import unittest

import pytest

from sc_client.constants import sc_types as t
from sc_client.models import ScType
from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError


class TestScType(unittest.TestCase):
    # pylint: disable=too-many-public-methods

    @classmethod
    def setUpClass(cls) -> None:
        cls.types = {
            t.UNKNOWN,
            t.EDGE_U_COMMON,
            t.EDGE_D_COMMON,
            t.EDGE_ACCESS,
            t.EDGE_U_COMMON_CONST,
            t.EDGE_D_COMMON_CONST,
            t.EDGE_U_COMMON_VAR,
            t.EDGE_D_COMMON_VAR,
            t.EDGE_ACCESS_CONST_POS_PERM,
            t.EDGE_ACCESS_CONST_NEG_PERM,
            t.EDGE_ACCESS_CONST_FUZ_PERM,
            t.EDGE_ACCESS_CONST_POS_TEMP,
            t.EDGE_ACCESS_CONST_NEG_TEMP,
            t.EDGE_ACCESS_CONST_FUZ_TEMP,
            t.EDGE_ACCESS_VAR_POS_PERM,
            t.EDGE_ACCESS_VAR_NEG_PERM,
            t.EDGE_ACCESS_VAR_FUZ_PERM,
            t.EDGE_ACCESS_VAR_POS_TEMP,
            t.EDGE_ACCESS_VAR_NEG_TEMP,
            t.EDGE_ACCESS_VAR_FUZ_TEMP,
            t.NODE,
            t.LINK,
            t.CONST,
            t.VAR,
            t.NODE_CONST,
            t.NODE_VAR,
            t.LINK_CONST,
            t.LINK_VAR,
            t.NODE_STRUCT,
            t.NODE_TUPLE,
            t.NODE_ROLE,
            t.NODE_NOROLE,
            t.NODE_CLASS,
            t.NODE_ABSTRACT,
            t.NODE_MATERIAL,
            t.NODE_CONST_CLASS,
            t.NODE_CONST_ROLE,
            t.NODE_CONST_NOROLE,
            t.NODE_CONST_TUPLE,
            t.NODE_CONST_STRUCT,
            t.NODE_CONST_ABSTRACT,
            t.NODE_CONST_MATERIAL,
            t.NODE_VAR_CLASS,
            t.NODE_VAR_ROLE,
            t.NODE_VAR_NOROLE,
            t.NODE_VAR_TUPLE,
            t.NODE_VAR_STRUCT,
            t.NODE_VAR_ABSTRACT,
            t.NODE_VAR_MATERIAL,
        }

    def test_init(self):
        self.assertEqual(ScType().value, 0)
        self.assertEqual(ScType(0).value, 0)
        self.assertEqual(ScType(1).value, 1)
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.INT_TYPE_INITIALIZATION):
            # noinspection PyTypeChecker
            ScType("not int")

    def test_is_valid(self):
        self.assertFalse(ScType().is_valid())
        self.assertFalse(bool(ScType()))
        self.assertFalse(ScType(0).is_valid())
        self.assertFalse(bool(ScType(0)))
        self.assertTrue(ScType(1).is_valid())
        self.assertTrue(bool(ScType(1)))

    def test_is_equal(self):
        self.assertTrue(ScType().is_equal(ScType()))
        self.assertEqual(ScType(), ScType())
        self.assertTrue(ScType(1).is_equal(ScType(1)))
        self.assertEqual(ScType(1), ScType(1))
        addr = ScType(2)
        self.assertTrue(addr.is_equal(addr))
        self.assertEqual(addr, addr)
        self.assertFalse(ScType(1).is_equal(ScType(2)))
        self.assertNotEqual(ScType(1), ScType(2))

    def test_hash(self):
        self.assertEqual(hash(ScType(1)), hash(ScType(1)))
        self.assertNotEqual(hash(ScType(0)), hash(ScType(1)))
        self.assertNotEqual(hash(ScType(3)), hash(3))

    def test_rshift(self):
        self.assertEqual(ScType(1) >> "alias", (ScType(1), "alias"))

    def test_repr(self):
        self.assertEqual(repr(ScType(0x821)), "ScType(0x821)")

    def test_is_node(self):
        node_types = {
            t.NODE,
            t.NODE_CLASS,
            t.NODE_ROLE,
            t.NODE_NOROLE,
            t.NODE_TUPLE,
            t.NODE_STRUCT,
            t.NODE_ABSTRACT,
            t.NODE_MATERIAL,
            t.NODE_CONST,
            t.NODE_CONST_CLASS,
            t.NODE_CONST_ROLE,
            t.NODE_CONST_NOROLE,
            t.NODE_CONST_TUPLE,
            t.NODE_CONST_STRUCT,
            t.NODE_CONST_ABSTRACT,
            t.NODE_CONST_MATERIAL,
            t.NODE_VAR,
            t.NODE_VAR_CLASS,
            t.NODE_VAR_ROLE,
            t.NODE_VAR_NOROLE,
            t.NODE_VAR_TUPLE,
            t.NODE_VAR_STRUCT,
            t.NODE_VAR_ABSTRACT,
            t.NODE_VAR_MATERIAL,
        }
        for sc_type in node_types:
            assert sc_type.is_node()
        for sc_type in self.types.difference(node_types):
            assert sc_type.is_node() is False

    def test_is_edge(self):
        edge_types = {
            t.EDGE_U_COMMON,
            t.EDGE_D_COMMON,
            t.EDGE_ACCESS,
            t.EDGE_U_COMMON_CONST,
            t.EDGE_D_COMMON_CONST,
            t.EDGE_U_COMMON_VAR,
            t.EDGE_D_COMMON_VAR,
            t.EDGE_ACCESS_CONST_POS_PERM,
            t.EDGE_ACCESS_CONST_NEG_PERM,
            t.EDGE_ACCESS_CONST_FUZ_PERM,
            t.EDGE_ACCESS_CONST_POS_TEMP,
            t.EDGE_ACCESS_CONST_NEG_TEMP,
            t.EDGE_ACCESS_CONST_FUZ_TEMP,
            t.EDGE_ACCESS_VAR_POS_PERM,
            t.EDGE_ACCESS_VAR_NEG_PERM,
            t.EDGE_ACCESS_VAR_FUZ_PERM,
            t.EDGE_ACCESS_VAR_POS_TEMP,
            t.EDGE_ACCESS_VAR_NEG_TEMP,
            t.EDGE_ACCESS_VAR_FUZ_TEMP,
        }
        for sc_type in edge_types:
            assert sc_type.is_edge()
        for sc_type in self.types.difference(edge_types):
            assert sc_type.is_edge() is False

    def test_is_link(self):
        link_types = {t.LINK_CONST, t.LINK_VAR, t.LINK}
        for sc_type in link_types:
            assert sc_type.is_link()
        for sc_type in self.types.difference(link_types):
            assert sc_type.is_link() is False

    def test_is_const(self):
        const_types = {
            t.CONST,
            t.NODE_CONST,
            t.LINK_CONST,
            t.EDGE_U_COMMON_CONST,
            t.EDGE_D_COMMON_CONST,
            t.EDGE_ACCESS_CONST_POS_PERM,
            t.EDGE_ACCESS_CONST_NEG_PERM,
            t.EDGE_ACCESS_CONST_FUZ_PERM,
            t.EDGE_ACCESS_CONST_POS_TEMP,
            t.EDGE_ACCESS_CONST_NEG_TEMP,
            t.EDGE_ACCESS_CONST_FUZ_TEMP,
            t.NODE_CONST_CLASS,
            t.NODE_CONST_ROLE,
            t.NODE_CONST_NOROLE,
            t.NODE_CONST_TUPLE,
            t.NODE_CONST_STRUCT,
            t.NODE_CONST_ABSTRACT,
            t.NODE_CONST_MATERIAL,
        }
        for sc_type in const_types:
            assert sc_type.is_const()

        for sc_type in self.types.difference(const_types):
            assert sc_type.is_const() is False

    def test_is_var(self):
        var_types = {
            t.VAR,
            t.NODE_VAR,
            t.LINK_VAR,
            t.EDGE_U_COMMON_VAR,
            t.EDGE_D_COMMON_VAR,
            t.EDGE_ACCESS_VAR_POS_PERM,
            t.EDGE_ACCESS_VAR_NEG_PERM,
            t.EDGE_ACCESS_VAR_FUZ_PERM,
            t.EDGE_ACCESS_VAR_POS_TEMP,
            t.EDGE_ACCESS_VAR_NEG_TEMP,
            t.EDGE_ACCESS_VAR_FUZ_TEMP,
            t.NODE_VAR_CLASS,
            t.NODE_VAR_ROLE,
            t.NODE_VAR_NOROLE,
            t.NODE_VAR_TUPLE,
            t.NODE_VAR_STRUCT,
            t.NODE_VAR_ABSTRACT,
            t.NODE_VAR_MATERIAL,
        }
        for sc_type in var_types:
            assert sc_type.is_var()

        for sc_type in self.types.difference(var_types):
            assert sc_type.is_var() is False

    def test_is_neg(self):
        neg_types = {
            t.EDGE_ACCESS_CONST_NEG_PERM,
            t.EDGE_ACCESS_CONST_NEG_TEMP,
            t.EDGE_ACCESS_VAR_NEG_PERM,
            t.EDGE_ACCESS_VAR_NEG_TEMP,
        }
        for sc_type in neg_types:
            assert sc_type.is_neg()

        for sc_type in self.types.difference(neg_types):
            assert sc_type.is_neg() is False

    def test_is_pos(self):
        pos_types = {
            t.EDGE_ACCESS_CONST_POS_PERM,
            t.EDGE_ACCESS_CONST_POS_TEMP,
            t.EDGE_ACCESS_VAR_POS_PERM,
            t.EDGE_ACCESS_VAR_POS_TEMP,
        }
        for sc_type in pos_types:
            assert sc_type.is_pos()

        for sc_type in self.types.difference(pos_types):
            assert sc_type.is_pos() is False

    def test_is_fuz(self):
        fuz_types = {
            t.EDGE_ACCESS_CONST_FUZ_PERM,
            t.EDGE_ACCESS_CONST_FUZ_TEMP,
            t.EDGE_ACCESS_VAR_FUZ_PERM,
            t.EDGE_ACCESS_VAR_FUZ_TEMP,
        }
        for sc_type in fuz_types:
            assert sc_type.is_fuz()

        for sc_type in self.types.difference(fuz_types):
            assert sc_type.is_fuz() is False

    def test_is_perm(self):
        perm_types = {
            t.EDGE_ACCESS_CONST_POS_PERM,
            t.EDGE_ACCESS_CONST_NEG_PERM,
            t.EDGE_ACCESS_CONST_FUZ_PERM,
            t.EDGE_ACCESS_VAR_POS_PERM,
            t.EDGE_ACCESS_VAR_NEG_PERM,
            t.EDGE_ACCESS_VAR_FUZ_PERM,
        }
        for sc_type in perm_types:
            assert sc_type.is_perm()

        for sc_type in self.types.difference(perm_types):
            assert sc_type.is_perm() is False

    def test_is_temp(self):
        temp_types = {
            t.EDGE_ACCESS_CONST_POS_TEMP,
            t.EDGE_ACCESS_CONST_NEG_TEMP,
            t.EDGE_ACCESS_CONST_FUZ_TEMP,
            t.EDGE_ACCESS_VAR_POS_TEMP,
            t.EDGE_ACCESS_VAR_NEG_TEMP,
            t.EDGE_ACCESS_VAR_FUZ_TEMP,
        }
        for sc_type in temp_types:
            assert sc_type.is_temp()

        for sc_type in self.types.difference(temp_types):
            assert sc_type.is_temp() is False

    def test_is_tuple(self):
        tuple_types = {t.NODE_TUPLE, t.NODE_CONST_TUPLE, t.NODE_VAR_TUPLE}
        for sc_type in tuple_types:
            assert sc_type.is_tuple()

        for sc_type in self.types.difference(tuple_types):
            assert sc_type.is_tuple() is False

    def test_is_struct(self):
        struct_types = {t.NODE_STRUCT, t.NODE_CONST_STRUCT, t.NODE_VAR_STRUCT}
        for sc_type in struct_types:
            assert sc_type.is_struct()

        for sc_type in self.types.difference(struct_types):
            assert sc_type.is_struct() is False

    def test_is_role(self):
        role_types = {t.NODE_ROLE, t.NODE_CONST_ROLE, t.NODE_VAR_ROLE}
        for sc_type in role_types:
            assert sc_type.is_role()

        for sc_type in self.types.difference(role_types):
            assert sc_type.is_role() is False

    def test_is_norole(self):
        norole_types = {t.NODE_NOROLE, t.NODE_CONST_NOROLE, t.NODE_VAR_NOROLE}
        for sc_type in norole_types:
            assert sc_type.is_norole()

        for sc_type in self.types.difference(norole_types):
            assert sc_type.is_norole() is False

    def test_is_class(self):
        class_types = {t.NODE_CLASS, t.NODE_CONST_CLASS, t.NODE_VAR_CLASS}
        for sc_type in class_types:
            assert sc_type.is_class()

        for sc_type in self.types.difference(class_types):
            assert sc_type.is_class() is False

    def test_is_abstract(self):
        abstract_types = {t.NODE_ABSTRACT, t.NODE_CONST_ABSTRACT, t.NODE_VAR_ABSTRACT}
        for sc_type in abstract_types:
            assert sc_type.is_abstract()

        for sc_type in self.types.difference(abstract_types):
            assert sc_type.is_abstract() is False

    def test_is_material(self):
        material_types = {t.NODE_MATERIAL, t.NODE_CONST_MATERIAL, t.NODE_VAR_MATERIAL}
        for sc_type in material_types:
            assert sc_type.is_material()

        for sc_type in self.types.difference(material_types):
            assert sc_type.is_material() is False

    def test_change_const(self):
        assert t.CONST.change_const(True).is_const()
        assert t.CONST.change_const(False).is_const() is False
        assert t.CONST.change_const(True).is_var() is False
        assert t.CONST.change_const(False).is_var()

    def test_merge(self):
        assert t.NODE_CONST.merge(t.NODE_CLASS) == t.NODE_CONST_CLASS
        with pytest.raises(InvalidTypeError):
            assert t.CONST.merge(t.NODE) == t.NODE_CONST

    def test_has_constancy(self):
        assert t.NODE_CONST.has_constancy()
        assert t.NODE_VAR.has_constancy()
        assert t.NODE.has_constancy() is False
