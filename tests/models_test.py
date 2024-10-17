import unittest

import pytest

from sc_client.constants import ScType
from sc_client.constants import sc_type as t
from sc_client.constants.exceptions import CommonErrorMessages, InvalidTypeError
from sc_client.models import ScAddr


def init_logic(obj):
    assert obj().value == 0
    assert obj(0).value == 0
    assert obj(1).value == 1
    with pytest.raises(InvalidTypeError, match=CommonErrorMessages.INVALID_TYPE.value):
        obj("10")


def is_valid_logic(obj):
    assert obj().is_valid() is False and bool(obj()) is False
    assert obj(0).is_valid() is False and bool(obj(0)) is False
    assert obj(1).is_valid() and bool(obj(1))


def is_equal_logic(obj):
    assert obj().is_equal(obj()) and obj() == obj()
    assert obj(1000).is_equal(obj(1000)) and obj(1000) == obj(1000)
    addr = obj(2000)
    assert addr.is_equal(addr)
    assert addr != obj()


class TestScAddr(unittest.TestCase):
    def test_init(self):
        init_logic(ScAddr)

    def test_is_valid(self):
        is_valid_logic(ScAddr)

    def test_is_equal(self):
        is_equal_logic(ScAddr)


class TestScType(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.types = {
            t.UNKNOWN,
            t.NODE,
            t.CONNECTOR,
            t.COMMON_EDGE,
            t.ARC,
            t.COMMON_ARC,
            t.MEMBERSHIP_ARC,
            
            t.CONST,
            t.VAR,
            
            t.CONST_NODE,
            t.VAR_NODE,
            t.CONST_CONNECTOR,
            t.VAR_CONNECTOR,
            t.CONST_COMMON_EDGE,
            t.VAR_COMMON_EDGE,
            t.CONST_ARC,
            t.VAR_ARC,
            t.CONST_COMMON_ARC,
            t.VAR_COMMON_ARC,
            t.CONST_MEMBERSHIP_ARC,
            t.VAR_MEMBERSHIP_ARC,

            t.PERM_ARC,
            t.TEMP_ARC,

            t.CONST_PERM_ARC,
            t.VAR_PERM_ARC,
            t.CONST_TEMP_ARC,
            t.VAR_TEMP_ARC,

            t.ACTUAL_TEMP_ARC,
            t.INACTUAL_TEMP_ARC,

            t.CONST_ACTUAL_TEMP_ARC,
            t.VAR_ACTUAL_TEMP_ARC,
            t.CONST_INACTUAL_TEMP_ARC,
            t.VAR_INACTUAL_TEMP_ARC,

            t.POS_ARC,
            t.NEG_ARC,

            t.FUZ_ARC,

            t.CONST_POS_ARC,
            t.VAR_POS_ARC,

            t.PERM_POS_ARC,
            t.TEMP_POS_ARC,
            t.ACTUAL_TEMP_POS_ARC,
            t.INACTUAL_TEMP_POS_ARC,

            t.CONST_PERM_POS_ARC,
            t.CONST_TEMP_POS_ARC,
            t.CONST_ACTUAL_TEMP_POS_ARC,
            t.CONST_INACTUAL_TEMP_POS_ARC,

            t.VAR_PERM_POS_ARC,
            t.VAR_TEMP_POS_ARC,
            t.VAR_ACTUAL_TEMP_POS_ARC,
            t.VAR_INACTUAL_TEMP_POS_ARC,

            t.CONST_NEG_ARC,
            t.VAR_NEG_ARC,

            t.PERM_NEG_ARC,
            t.TEMP_NEG_ARC,
            t.ACTUAL_TEMP_NEG_ARC,
            t.INACTUAL_TEMP_NEG_ARC,

            t.CONST_PERM_NEG_ARC,
            t.CONST_TEMP_NEG_ARC,
            t.CONST_ACTUAL_TEMP_NEG_ARC,
            t.CONST_INACTUAL_TEMP_NEG_ARC,

            t.VAR_PERM_NEG_ARC,
            t.VAR_TEMP_NEG_ARC,
            t.VAR_ACTUAL_TEMP_NEG_ARC,
            t.VAR_INACTUAL_TEMP_NEG_ARC,

            t.CONST_FUZ_ARC,
            t.VAR_FUZ_ARC,

            t.NODE_LINK,
            t.NODE_LINK_CLASS,
            t.NODE_TUPLE,
            t.NODE_STRUCTURE,
            t.NODE_ROLE,
            t.NODE_NO_ROLE,
            t.NODE_CLASS, 
            t.NODE_SUPERCLASS, 
            t.NODE_MATERIAL,

            t.CONST_NODE_LINK, 
            t.CONST_NODE_LINK_CLASS, 
            t.CONST_NODE_TUPLE, 
            t.CONST_NODE_STRUCTURE, 
            t.CONST_NODE_ROLE, 
            t.CONST_NODE_NO_ROLE, 
            t.CONST_NODE_CLASS, 
            t.CONST_NODE_SUPERCLASS, 
            t.CONST_NODE_MATERIAL,

            t.VAR_NODE_LINK, 
            t.VAR_NODE_LINK_CLASS, 
            t.VAR_NODE_TUPLE, 
            t.VAR_NODE_STRUCTURE, 
            t.VAR_NODE_ROLE, 
            t.VAR_NODE_NO_ROLE, 
            t.VAR_NODE_CLASS, 
            t.VAR_NODE_SUPERCLASS, 
            t.VAR_NODE_MATERIAL
        }

    def test_init(self):
        init_logic(ScType)

    def test_is_valid(self):
        is_valid_logic(ScType)

    def test_is_equal(self):
        is_equal_logic(ScType)

    def test_is_node(self):
        node_types = {
            t.NODE,
            t.NODE_LINK,
            t.NODE_LINK_CLASS,
            t.NODE_TUPLE,
            t.NODE_STRUCTURE,
            t.NODE_ROLE,
            t.NODE_NO_ROLE,
            t.NODE_CLASS, 
            t.NODE_SUPERCLASS, 
            t.NODE_MATERIAL,

            t.CONST_NODE,
            t.CONST_NODE_LINK, 
            t.CONST_NODE_LINK_CLASS, 
            t.CONST_NODE_TUPLE, 
            t.CONST_NODE_STRUCTURE, 
            t.CONST_NODE_ROLE, 
            t.CONST_NODE_NO_ROLE, 
            t.CONST_NODE_CLASS, 
            t.CONST_NODE_SUPERCLASS, 
            t.CONST_NODE_MATERIAL,

            t.VAR_NODE,
            t.VAR_NODE_LINK, 
            t.VAR_NODE_LINK_CLASS, 
            t.VAR_NODE_TUPLE, 
            t.VAR_NODE_STRUCTURE, 
            t.VAR_NODE_ROLE, 
            t.VAR_NODE_NO_ROLE, 
            t.VAR_NODE_CLASS, 
            t.VAR_NODE_SUPERCLASS, 
            t.VAR_NODE_MATERIAL
        }
        for sc_type in node_types:
            assert sc_type.is_node()
        for sc_type in self.types.difference(node_types):
            assert sc_type.is_node() is False

    def test_is_connector(self):
        edge_types = {
            t.CONNECTOR,
            t.COMMON_EDGE,
            t.ARC,
            t.COMMON_ARC,
            t.MEMBERSHIP_ARC,

            t.CONST_CONNECTOR,
            t.VAR_CONNECTOR,
            t.CONST_COMMON_EDGE,
            t.VAR_COMMON_EDGE,
            t.CONST_ARC,
            t.VAR_ARC,
            t.CONST_COMMON_ARC,
            t.VAR_COMMON_ARC,
            t.CONST_MEMBERSHIP_ARC,
            t.VAR_MEMBERSHIP_ARC,

            t.PERM_ARC,
            t.TEMP_ARC,

            t.CONST_PERM_ARC,
            t.VAR_PERM_ARC,
            t.CONST_TEMP_ARC,
            t.VAR_TEMP_ARC,

            t.ACTUAL_TEMP_ARC,
            t.INACTUAL_TEMP_ARC,

            t.CONST_ACTUAL_TEMP_ARC,
            t.VAR_ACTUAL_TEMP_ARC,
            t.CONST_INACTUAL_TEMP_ARC,
            t.VAR_INACTUAL_TEMP_ARC,

            t.POS_ARC,
            t.NEG_ARC,

            t.FUZ_ARC,

            t.CONST_POS_ARC,
            t.VAR_POS_ARC,

            t.PERM_POS_ARC,
            t.TEMP_POS_ARC,
            t.ACTUAL_TEMP_POS_ARC,
            t.INACTUAL_TEMP_POS_ARC,

            t.CONST_PERM_POS_ARC,
            t.CONST_TEMP_POS_ARC,
            t.CONST_ACTUAL_TEMP_POS_ARC,
            t.CONST_INACTUAL_TEMP_POS_ARC,

            t.VAR_PERM_POS_ARC,
            t.VAR_TEMP_POS_ARC,
            t.VAR_ACTUAL_TEMP_POS_ARC,
            t.VAR_INACTUAL_TEMP_POS_ARC,

            t.CONST_NEG_ARC,
            t.VAR_NEG_ARC,

            t.PERM_NEG_ARC,
            t.TEMP_NEG_ARC,
            t.ACTUAL_TEMP_NEG_ARC,
            t.INACTUAL_TEMP_NEG_ARC,

            t.CONST_PERM_NEG_ARC,
            t.CONST_TEMP_NEG_ARC,
            t.CONST_ACTUAL_TEMP_NEG_ARC,
            t.CONST_INACTUAL_TEMP_NEG_ARC,

            t.VAR_PERM_NEG_ARC,
            t.VAR_TEMP_NEG_ARC,
            t.VAR_ACTUAL_TEMP_NEG_ARC,
            t.VAR_INACTUAL_TEMP_NEG_ARC,

            t.CONST_FUZ_ARC,
            t.VAR_FUZ_ARC,
        }
        for sc_type in edge_types:
            assert sc_type.is_edge()
        for sc_type in self.types.difference(edge_types):
            assert sc_type.is_edge() is False

    def test_is_link(self):
        link_types = {t.CONST_NODE_LINK, t.CONST_NODE_LINK_CLASS, t.VAR_NODE_LINK, t.VAR_NODE_LINK_CLASS, t.NODE_LINK, t.NODE_LINK_CLASS}
        for sc_type in link_types:
            assert sc_type.is_link()
        for sc_type in self.types.difference(link_types):
            assert sc_type.is_link() is False

    def test_is_const(self):
        const_types = {
            t.CONST,

            t.CONST_NODE,
            t.CONST_CONNECTOR,
            t.CONST_COMMON_EDGE,
            t.CONST_ARC,
            t.CONST_COMMON_ARC,
            t.CONST_MEMBERSHIP_ARC,

            t.CONST_PERM_ARC,
            t.CONST_TEMP_ARC,

            t.CONST_ACTUAL_TEMP_ARC,
            t.CONST_INACTUAL_TEMP_ARC,

            t.CONST_POS_ARC,

            t.CONST_PERM_POS_ARC,
            t.CONST_TEMP_POS_ARC,
            t.CONST_ACTUAL_TEMP_POS_ARC,
            t.CONST_INACTUAL_TEMP_POS_ARC,

            t.CONST_NEG_ARC,

            t.CONST_PERM_NEG_ARC,
            t.CONST_TEMP_NEG_ARC,
            t.CONST_ACTUAL_TEMP_NEG_ARC,
            t.CONST_INACTUAL_TEMP_NEG_ARC,

            t.CONST_FUZ_ARC,
            
            t.CONST_NODE_LINK, 
            t.CONST_NODE_LINK_CLASS, 
            t.CONST_NODE_TUPLE, 
            t.CONST_NODE_STRUCTURE, 
            t.CONST_NODE_ROLE, 
            t.CONST_NODE_NO_ROLE, 
            t.CONST_NODE_CLASS, 
            t.CONST_NODE_SUPERCLASS, 
            t.CONST_NODE_MATERIAL,
        }
        for sc_type in const_types:
            assert sc_type.is_const()

        for sc_type in self.types.difference(const_types):
            assert sc_type.is_const() is False

    def test_is_var(self):
        var_types = {
            t.VAR,

            t.VAR_NODE,
            t.VAR_CONNECTOR,
            t.VAR_COMMON_EDGE,
            t.VAR_ARC,
            t.VAR_COMMON_ARC,
            t.VAR_MEMBERSHIP_ARC,

            t.VAR_PERM_ARC,
            t.VAR_TEMP_ARC,

            t.VAR_ACTUAL_TEMP_ARC,
            t.VAR_INACTUAL_TEMP_ARC,

            t.VAR_POS_ARC,

            t.VAR_PERM_POS_ARC,
            t.VAR_TEMP_POS_ARC,
            t.VAR_ACTUAL_TEMP_POS_ARC,
            t.VAR_INACTUAL_TEMP_POS_ARC,

            t.VAR_NEG_ARC,

            t.VAR_PERM_NEG_ARC,
            t.VAR_TEMP_NEG_ARC,
            t.VAR_ACTUAL_TEMP_NEG_ARC,
            t.VAR_INACTUAL_TEMP_NEG_ARC,

            t.VAR_FUZ_ARC,
            
            t.VAR_NODE_LINK, 
            t.VAR_NODE_LINK_CLASS, 
            t.VAR_NODE_TUPLE, 
            t.VAR_NODE_STRUCTURE, 
            t.VAR_NODE_ROLE, 
            t.VAR_NODE_NO_ROLE, 
            t.VAR_NODE_CLASS, 
            t.VAR_NODE_SUPERCLASS, 
            t.VAR_NODE_MATERIAL,
        }
        for sc_type in var_types:
            assert sc_type.is_var()

        for sc_type in self.types.difference(var_types):
            assert sc_type.is_var() is False

    def test_is_neg(self):
        neg_types = {
            t.NEG_ARC,
            t.CONST_NEG_ARC,
            t.VAR_NEG_ARC,
            t.PERM_NEG_ARC,
            t.CONST_PERM_NEG_ARC,
            t.VAR_PERM_NEG_ARC,
            t.TEMP_NEG_ARC,
            t.ACTUAL_TEMP_NEG_ARC,
            t.INACTUAL_TEMP_NEG_ARC,
            t.CONST_TEMP_NEG_ARC,
            t.VAR_TEMP_NEG_ARC,
            t.CONST_ACTUAL_TEMP_NEG_ARC,
            t.VAR_ACTUAL_TEMP_NEG_ARC,
            t.CONST_INACTUAL_TEMP_NEG_ARC,
            t.VAR_INACTUAL_TEMP_NEG_ARC
        }
        for sc_type in neg_types:
            assert sc_type.is_neg()

        for sc_type in self.types.difference(neg_types):
            assert sc_type.is_neg() is False

    def test_is_pos(self):
        pos_types = {
            t.POS_ARC,
            t.CONST_POS_ARC,
            t.VAR_POS_ARC,
            t.PERM_POS_ARC,
            t.CONST_PERM_POS_ARC,
            t.VAR_PERM_POS_ARC,
            t.TEMP_POS_ARC,
            t.ACTUAL_TEMP_POS_ARC,
            t.INACTUAL_TEMP_POS_ARC,
            t.CONST_TEMP_POS_ARC,
            t.VAR_TEMP_POS_ARC,
            t.CONST_ACTUAL_TEMP_POS_ARC,
            t.VAR_ACTUAL_TEMP_POS_ARC,
            t.CONST_INACTUAL_TEMP_POS_ARC,
            t.VAR_INACTUAL_TEMP_POS_ARC
        }
        for sc_type in pos_types:
            assert sc_type.is_pos()

        for sc_type in self.types.difference(pos_types):
            assert sc_type.is_pos() is False

    def test_is_fuz(self):
        fuz_types = {
            t.FUZ_ARC,
            t.CONST_FUZ_ARC,
            t.VAR_FUZ_ARC
        }
        for sc_type in fuz_types:
            assert sc_type.is_fuz()

        for sc_type in self.types.difference(fuz_types):
            assert sc_type.is_fuz() is False

    def test_is_perm(self):
        perm_types = {
            t.PERM_ARC,
            t.CONST_PERM_ARC,
            t.VAR_PERM_ARC,
            t.PERM_POS_ARC,
            t.PERM_NEG_ARC,
            t.CONST_PERM_POS_ARC,
            t.VAR_PERM_POS_ARC,
            t.CONST_PERM_NEG_ARC,
            t.VAR_PERM_NEG_ARC,
        }
        for sc_type in perm_types:
            assert sc_type.is_perm()

        for sc_type in self.types.difference(perm_types):
            assert sc_type.is_perm() is False

    def test_is_temp(self):
        temp_types = {
            t.TEMP_ARC,
            t.ACTUAL_TEMP_ARC,
            t.INACTUAL_TEMP_ARC,
            t.CONST_TEMP_ARC,
            t.VAR_TEMP_ARC,
            t.CONST_ACTUAL_TEMP_ARC,
            t.VAR_ACTUAL_TEMP_ARC,
            t.CONST_INACTUAL_TEMP_ARC,
            t.VAR_INACTUAL_TEMP_ARC,
            t.TEMP_POS_ARC,
            t.TEMP_NEG_ARC,
            t.ACTUAL_TEMP_POS_ARC,
            t.ACTUAL_TEMP_NEG_ARC,
            t.INACTUAL_TEMP_POS_ARC,
            t.INACTUAL_TEMP_NEG_ARC,
            t.CONST_TEMP_POS_ARC,
            t.VAR_TEMP_POS_ARC,
            t.CONST_TEMP_NEG_ARC,
            t.VAR_TEMP_NEG_ARC,
            t.CONST_ACTUAL_TEMP_POS_ARC,
            t.VAR_ACTUAL_TEMP_POS_ARC,
            t.CONST_ACTUAL_TEMP_NEG_ARC,
            t.VAR_ACTUAL_TEMP_NEG_ARC,
            t.CONST_INACTUAL_TEMP_POS_ARC,
            t.VAR_INACTUAL_TEMP_POS_ARC,
            t.CONST_INACTUAL_TEMP_NEG_ARC,
            t.VAR_INACTUAL_TEMP_NEG_ARC
        }
        for sc_type in temp_types:
            assert sc_type.is_temp()

        for sc_type in self.types.difference(temp_types):
            assert sc_type.is_temp() is False

    def test_is_actual(self):
        actual_types = {
            t.ACTUAL_TEMP_ARC,
            t.CONST_ACTUAL_TEMP_ARC,
            t.VAR_ACTUAL_TEMP_ARC,
            t.ACTUAL_TEMP_POS_ARC,
            t.ACTUAL_TEMP_NEG_ARC,
            t.CONST_ACTUAL_TEMP_POS_ARC,
            t.VAR_ACTUAL_TEMP_POS_ARC,
            t.CONST_ACTUAL_TEMP_NEG_ARC,
            t.VAR_ACTUAL_TEMP_NEG_ARC,
        }
        for sc_type in actual_types:
            assert sc_type.is_actual()

        for sc_type in self.types.difference(actual_types):
            assert sc_type.is_actual() is False

    def test_is_inactual(self):
        inactual_types = {            
            t.INACTUAL_TEMP_ARC,
            t.CONST_INACTUAL_TEMP_ARC,
            t.VAR_INACTUAL_TEMP_ARC,
            t.INACTUAL_TEMP_POS_ARC,
            t.INACTUAL_TEMP_NEG_ARC,
            t.CONST_INACTUAL_TEMP_POS_ARC,
            t.VAR_INACTUAL_TEMP_POS_ARC,
            t.CONST_INACTUAL_TEMP_NEG_ARC,
            t.VAR_INACTUAL_TEMP_NEG_ARC,
        }
        for sc_type in inactual_types:
            assert sc_type.is_inactual()

        for sc_type in self.types.difference(inactual_types):
            assert sc_type.is_inactual() is False

    def test_is_tuple(self):
        tuple_types = {t.NODE_TUPLE, t.CONST_NODE_TUPLE, t.VAR_NODE_TUPLE}
        for sc_type in tuple_types:
            assert sc_type.is_tuple()

        for sc_type in self.types.difference(tuple_types):
            assert sc_type.is_tuple() is False

    def test_is_structure(self):
        structure_types = {t.NODE_STRUCTURE, t.CONST_NODE_STRUCTURE, t.VAR_NODE_STRUCTURE}
        for sc_type in structure_types:
            assert sc_type.is_structure()

        for sc_type in self.types.difference(structure_types):
            assert sc_type.is_structure() is False

    def test_is_role(self):
        role_types = {t.NODE_ROLE, t.CONST_NODE_ROLE, t.VAR_NODE_ROLE}
        for sc_type in role_types:
            assert sc_type.is_role()

        for sc_type in self.types.difference(role_types):
            assert sc_type.is_role() is False

    def test_is_no_role(self):
        no_role_types = {t.NODE_NO_ROLE, t.CONST_NODE_NO_ROLE, t.VAR_NODE_NO_ROLE}
        for sc_type in no_role_types:
            assert sc_type.is_no_role()

        for sc_type in self.types.difference(no_role_types):
            assert sc_type.is_no_role() is False

    def test_is_class(self):
        class_types = {t.NODE_CLASS, t.CONST_NODE_CLASS, t.VAR_NODE_CLASS}
        for sc_type in class_types:
            assert sc_type.is_class()

        for sc_type in self.types.difference(class_types):
            assert sc_type.is_class() is False
    
    def test_is_class(self):
        superclass_types = {t.NODE_SUPERCLASS, t.CONST_NODE_SUPERCLASS, t.VAR_NODE_SUPERCLASS}
        for sc_type in superclass_types:
            assert sc_type.is_superclass()

        for sc_type in self.types.difference(superclass_types):
            assert sc_type.is_superclass() is False

    def test_is_material(self):
        material_types = {t.NODE_MATERIAL, t.CONST_NODE_MATERIAL, t.VAR_NODE_MATERIAL}
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
        assert t.UNKNOWN.merge(t.NODE) == t.NODE
        assert t.NODE.merge(t.CONST_NODE) == t.CONST_NODE
        assert t.CONST_NODE.merge(t.CONST_NODE_CLASS) == t.CONST_NODE_CLASS
        assert t.NODE.merge(t.NODE_LINK_CLASS) == t.NODE_LINK_CLASS
        assert t.CONNECTOR.merge(t.CONST_MEMBERSHIP_ARC) == t.CONST_MEMBERSHIP_ARC
        with pytest.raises(InvalidTypeError, match=CommonErrorMessages.INVALID_TYPE.value):
            t.CONST.merge(t.NODE)
        with pytest.raises(InvalidTypeError, match=CommonErrorMessages.INVALID_TYPE.value):
            t.CONNECTOR.merge(t.NODE)
        with pytest.raises(InvalidTypeError, match=CommonErrorMessages.INVALID_TYPE.value):
            t.COMMON_EDGE.merge(t.COMMON_ARC)
        with pytest.raises(InvalidTypeError, match=CommonErrorMessages.INVALID_TYPE.value):
            t.COMMON_ARC.merge(t.MEMBERSHIP_ARC)

    def test_has_constancy(self):
        assert t.CONST_NODE.has_constancy()
        assert t.VAR_NODE.has_constancy()
        assert t.NODE.has_constancy() is False
