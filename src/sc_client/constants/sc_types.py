"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from __future__ import annotations

from sc_client.constants.exceptions import InvalidTypeError

SC_TYPE_NODE = 0x1
SC_TYPE_LINK = 0x2
SC_TYPE_UEDGE_COMMON = 0x4
SC_TYPE_DEDGE_COMMON = 0x8
SC_TYPE_EDGE_ACCESS = 0x10

SC_TYPE_CONST = 0x20
SC_TYPE_VAR = 0x40

SC_TYPE_EDGE_POS = 0x80
SC_TYPE_EDGE_NEG = 0x100
SC_TYPE_EDGE_FUZ = 0x200

SC_TYPE_EDGE_TEMP = 0x400
SC_TYPE_EDGE_PERM = 0x800

SC_TYPE_NODE_TUPLE = 0x80
SC_TYPE_NODE_STRUCT = 0x100
SC_TYPE_NODE_ROLE = 0x200
SC_TYPE_NODE_NOROLE = 0x400
SC_TYPE_NODE_CLASS = 0x800

SC_TYPE_NODE_ABSTRACT = 0x1000
SC_TYPE_NODE_MATERIAL = 0x2000

SC_TYPE_ARC_POS_CONST_PERM = SC_TYPE_EDGE_ACCESS | SC_TYPE_CONST | SC_TYPE_EDGE_POS | SC_TYPE_EDGE_PERM
SC_TYPE_ARC_POS_VAR_PERM = SC_TYPE_EDGE_ACCESS | SC_TYPE_VAR | SC_TYPE_EDGE_POS | SC_TYPE_EDGE_PERM

SC_TYPE_ELEMENT_MASK = SC_TYPE_NODE | SC_TYPE_LINK | SC_TYPE_UEDGE_COMMON | SC_TYPE_DEDGE_COMMON | SC_TYPE_EDGE_ACCESS
SC_TYPE_CONSTANCY_MASK = SC_TYPE_CONST | SC_TYPE_VAR
SC_TYPE_POSITIVITY_MASK = SC_TYPE_EDGE_POS | SC_TYPE_EDGE_NEG | SC_TYPE_EDGE_FUZ
SC_TYPE_PERMANENCY_MASK = SC_TYPE_EDGE_PERM | SC_TYPE_EDGE_TEMP
SC_TYPE_NODE_STRUCT_MASK = (
    SC_TYPE_NODE_TUPLE
    | SC_TYPE_NODE_STRUCT
    | SC_TYPE_NODE_ROLE
    | SC_TYPE_NODE_NOROLE
    | SC_TYPE_NODE_CLASS
    | SC_TYPE_NODE_ABSTRACT
    | SC_TYPE_NODE_MATERIAL
)
SC_TYPE_EDGE_MASK = SC_TYPE_EDGE_ACCESS | SC_TYPE_DEDGE_COMMON | SC_TYPE_UEDGE_COMMON


class ScType:
    def __init__(self, value: int = 0):
        if not isinstance(value, int):
            raise InvalidTypeError("You should to use int type for ScType initialization")
        self.value = value

    def __repr__(self) -> str:
        return f"ScType({hex(self.value)})"

    def __hash__(self) -> int:
        return hash((self.value, self.__class__))

    def __eq__(self, other: ScType) -> bool:
        if isinstance(other, ScType):
            return self.value == other.value
        return NotImplemented

    def __bool__(self) -> bool:
        return self.value != 0

    def has_constancy(self) -> bool:
        return (self.value & SC_TYPE_CONSTANCY_MASK) != 0

    def is_node(self) -> bool:
        return (self.value & SC_TYPE_NODE) != 0

    def is_edge(self) -> bool:
        return (self.value & SC_TYPE_EDGE_MASK) != 0

    def is_link(self) -> bool:
        return (self.value & SC_TYPE_LINK) != 0

    def is_const(self) -> bool:
        return (self.value & SC_TYPE_CONST) != 0

    def is_var(self) -> bool:
        return (self.value & SC_TYPE_VAR) != 0

    def is_pos(self) -> bool:
        return (self.value & SC_TYPE_EDGE_POS) != 0 and (self.value & SC_TYPE_EDGE_ACCESS) != 0

    def is_neg(self) -> bool:
        return (self.value & SC_TYPE_EDGE_NEG) != 0 and (self.value & SC_TYPE_EDGE_ACCESS) != 0

    def is_fuz(self) -> bool:
        return (self.value & SC_TYPE_EDGE_FUZ) != 0 and (self.value & SC_TYPE_EDGE_ACCESS) != 0

    def is_perm(self) -> bool:
        return (self.value & SC_TYPE_EDGE_PERM) != 0 and (self.value & SC_TYPE_EDGE_ACCESS) != 0

    def is_temp(self) -> bool:
        return (self.value & SC_TYPE_EDGE_TEMP) != 0 and (self.value & SC_TYPE_EDGE_ACCESS) != 0

    def is_tuple(self) -> bool:
        return (self.value & SC_TYPE_NODE_TUPLE) != 0 and (self.value & SC_TYPE_NODE) != 0

    def is_struct(self) -> bool:
        return (self.value & SC_TYPE_NODE_STRUCT) != 0 and (self.value & SC_TYPE_NODE) != 0

    def is_role(self) -> bool:
        return (self.value & SC_TYPE_NODE_ROLE) != 0 and (self.value & SC_TYPE_NODE) != 0

    def is_norole(self) -> bool:
        return (self.value & SC_TYPE_NODE_NOROLE) != 0 and (self.value & SC_TYPE_NODE) != 0

    def is_class(self) -> bool:
        return (self.value & SC_TYPE_NODE_CLASS) != 0 and (self.value & SC_TYPE_NODE) != 0

    def is_abstract(self) -> bool:
        return (self.value & SC_TYPE_NODE_ABSTRACT) != 0 and (self.value & SC_TYPE_NODE) != 0

    def is_material(self) -> bool:
        return (self.value & SC_TYPE_NODE_MATERIAL) != 0 and (self.value & SC_TYPE_NODE) != 0

    def is_valid(self) -> bool:
        return self.__bool__()

    def is_equal(self, other: ScType) -> bool:
        return self.__eq__(other)

    def merge(self, other: ScType) -> ScType:
        t1 = self.value & SC_TYPE_ELEMENT_MASK
        t2 = other.value & SC_TYPE_ELEMENT_MASK
        if (t1 != 0 or t2 != 0) and (t1 != t2):
            raise InvalidTypeError()
        return ScType(self.value | other.value)

    def change_const(self, is_const: bool) -> ScType:
        v = self.value & ~SC_TYPE_CONSTANCY_MASK
        return ScType(v | (SC_TYPE_CONST if is_const else SC_TYPE_VAR))


EDGE_U_COMMON = ScType(SC_TYPE_UEDGE_COMMON)
EDGE_D_COMMON = ScType(SC_TYPE_DEDGE_COMMON)

EDGE_U_COMMON_CONST = ScType(SC_TYPE_UEDGE_COMMON | SC_TYPE_CONST)
EDGE_D_COMMON_CONST = ScType(SC_TYPE_DEDGE_COMMON | SC_TYPE_CONST)
EDGE_U_COMMON_VAR = ScType(SC_TYPE_UEDGE_COMMON | SC_TYPE_VAR)
EDGE_D_COMMON_VAR = ScType(SC_TYPE_DEDGE_COMMON | SC_TYPE_VAR)

EDGE_ACCESS = ScType(SC_TYPE_EDGE_ACCESS)
EDGE_ACCESS_CONST_POS_PERM = ScType(SC_TYPE_CONST | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_PERM | SC_TYPE_EDGE_POS)
EDGE_ACCESS_CONST_NEG_PERM = ScType(SC_TYPE_CONST | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_PERM | SC_TYPE_EDGE_NEG)
EDGE_ACCESS_CONST_FUZ_PERM = ScType(SC_TYPE_CONST | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_PERM | SC_TYPE_EDGE_FUZ)
EDGE_ACCESS_CONST_POS_TEMP = ScType(SC_TYPE_CONST | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_TEMP | SC_TYPE_EDGE_POS)
EDGE_ACCESS_CONST_NEG_TEMP = ScType(SC_TYPE_CONST | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_TEMP | SC_TYPE_EDGE_NEG)
EDGE_ACCESS_CONST_FUZ_TEMP = ScType(SC_TYPE_CONST | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_TEMP | SC_TYPE_EDGE_FUZ)

EDGE_ACCESS_VAR_POS_PERM = ScType(SC_TYPE_VAR | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_PERM | SC_TYPE_EDGE_POS)
EDGE_ACCESS_VAR_NEG_PERM = ScType(SC_TYPE_VAR | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_PERM | SC_TYPE_EDGE_NEG)
EDGE_ACCESS_VAR_FUZ_PERM = ScType(SC_TYPE_VAR | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_PERM | SC_TYPE_EDGE_FUZ)
EDGE_ACCESS_VAR_POS_TEMP = ScType(SC_TYPE_VAR | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_TEMP | SC_TYPE_EDGE_POS)
EDGE_ACCESS_VAR_NEG_TEMP = ScType(SC_TYPE_VAR | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_TEMP | SC_TYPE_EDGE_NEG)
EDGE_ACCESS_VAR_FUZ_TEMP = ScType(SC_TYPE_VAR | SC_TYPE_EDGE_ACCESS | SC_TYPE_EDGE_TEMP | SC_TYPE_EDGE_FUZ)

CONST = ScType(SC_TYPE_CONST)
VAR = ScType(SC_TYPE_VAR)

NODE = ScType(SC_TYPE_NODE)
LINK = ScType(SC_TYPE_LINK)
UNKNOWN = ScType()

NODE_CONST = ScType(SC_TYPE_NODE | SC_TYPE_CONST)
NODE_VAR = ScType(SC_TYPE_NODE | SC_TYPE_VAR)

LINK_CONST = ScType(SC_TYPE_LINK | SC_TYPE_CONST)
LINK_VAR = ScType(SC_TYPE_LINK | SC_TYPE_VAR)

NODE_STRUCT = ScType(SC_TYPE_NODE | SC_TYPE_NODE_STRUCT)
NODE_TUPLE = ScType(SC_TYPE_NODE | SC_TYPE_NODE_TUPLE)
NODE_ROLE = ScType(SC_TYPE_NODE | SC_TYPE_NODE_ROLE)
NODE_NOROLE = ScType(SC_TYPE_NODE | SC_TYPE_NODE_NOROLE)
NODE_CLASS = ScType(SC_TYPE_NODE | SC_TYPE_NODE_CLASS)
NODE_ABSTRACT = ScType(SC_TYPE_NODE | SC_TYPE_NODE_ABSTRACT)
NODE_MATERIAL = ScType(SC_TYPE_NODE | SC_TYPE_NODE_MATERIAL)

NODE_CONST_STRUCT = ScType(SC_TYPE_NODE | SC_TYPE_CONST | SC_TYPE_NODE_STRUCT)
NODE_CONST_TUPLE = ScType(SC_TYPE_NODE | SC_TYPE_CONST | SC_TYPE_NODE_TUPLE)
NODE_CONST_ROLE = ScType(SC_TYPE_NODE | SC_TYPE_CONST | SC_TYPE_NODE_ROLE)
NODE_CONST_NOROLE = ScType(SC_TYPE_NODE | SC_TYPE_CONST | SC_TYPE_NODE_NOROLE)
NODE_CONST_CLASS = ScType(SC_TYPE_NODE | SC_TYPE_CONST | SC_TYPE_NODE_CLASS)
NODE_CONST_ABSTRACT = ScType(SC_TYPE_NODE | SC_TYPE_CONST | SC_TYPE_NODE_ABSTRACT)
NODE_CONST_MATERIAL = ScType(SC_TYPE_NODE | SC_TYPE_CONST | SC_TYPE_NODE_MATERIAL)

NODE_VAR_STRUCT = ScType(SC_TYPE_NODE | SC_TYPE_VAR | SC_TYPE_NODE_STRUCT)
NODE_VAR_TUPLE = ScType(SC_TYPE_NODE | SC_TYPE_VAR | SC_TYPE_NODE_TUPLE)
NODE_VAR_ROLE = ScType(SC_TYPE_NODE | SC_TYPE_VAR | SC_TYPE_NODE_ROLE)
NODE_VAR_NOROLE = ScType(SC_TYPE_NODE | SC_TYPE_VAR | SC_TYPE_NODE_NOROLE)
NODE_VAR_CLASS = ScType(SC_TYPE_NODE | SC_TYPE_VAR | SC_TYPE_NODE_CLASS)
NODE_VAR_ABSTRACT = ScType(SC_TYPE_NODE | SC_TYPE_VAR | SC_TYPE_NODE_ABSTRACT)
NODE_VAR_MATERIAL = ScType(SC_TYPE_NODE | SC_TYPE_VAR | SC_TYPE_NODE_MATERIAL)
