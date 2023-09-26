from __future__ import annotations

from sc_client.constants import bitmasks
from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError


class ScType:
    # pylint: disable=too-many-public-methods

    def __init__(self, value: int = 0) -> None:
        if not isinstance(value, int):
            raise InvalidTypeError(ErrorNotes.INT_TYPE_INITIALIZATION)
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({hex(self.value)})"

    def __hash__(self) -> int:
        return hash((self.value, self.__class__))

    def __rshift__(self, alias: str) -> tuple[ScType, str]:
        return self, alias

    def __eq__(self, other: ScType) -> bool:
        return self.value == other.value

    def is_equal(self, other: ScType) -> bool:
        return self == other

    def __bool__(self) -> bool:
        return self.value != 0

    def is_valid(self) -> bool:
        return bool(self)

    def has_constancy(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_CONSTANCY_MASK) != 0

    def is_node(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_NODE) != 0

    def is_edge(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_EDGE_MASK) != 0

    def is_link(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_LINK) != 0

    def is_const(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_CONST) != 0

    def is_var(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_VAR) != 0

    def is_pos(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_EDGE_POS) != 0 and (self.value & bitmasks.SC_TYPE_EDGE_ACCESS) != 0

    def is_neg(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_EDGE_NEG) != 0 and (self.value & bitmasks.SC_TYPE_EDGE_ACCESS) != 0

    def is_fuz(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_EDGE_FUZ) != 0 and (self.value & bitmasks.SC_TYPE_EDGE_ACCESS) != 0

    def is_perm(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_EDGE_PERM) != 0 and (self.value & bitmasks.SC_TYPE_EDGE_ACCESS) != 0

    def is_temp(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_EDGE_TEMP) != 0 and (self.value & bitmasks.SC_TYPE_EDGE_ACCESS) != 0

    def is_tuple(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_NODE_TUPLE) != 0 and (self.value & bitmasks.SC_TYPE_NODE) != 0

    def is_struct(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_NODE_STRUCT) != 0 and (self.value & bitmasks.SC_TYPE_NODE) != 0

    def is_role(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_NODE_ROLE) != 0 and (self.value & bitmasks.SC_TYPE_NODE) != 0

    def is_norole(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_NODE_NOROLE) != 0 and (self.value & bitmasks.SC_TYPE_NODE) != 0

    def is_class(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_NODE_CLASS) != 0 and (self.value & bitmasks.SC_TYPE_NODE) != 0

    def is_abstract(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_NODE_ABSTRACT) != 0 and (self.value & bitmasks.SC_TYPE_NODE) != 0

    def is_material(self) -> bool:
        return (self.value & bitmasks.SC_TYPE_NODE_MATERIAL) != 0 and (self.value & bitmasks.SC_TYPE_NODE) != 0

    def merge(self, other: ScType) -> ScType:
        t1 = self.value & bitmasks.SC_TYPE_ELEMENT_MASK
        t2 = other.value & bitmasks.SC_TYPE_ELEMENT_MASK
        if (t1 != 0 or t2 != 0) and (t1 != t2):
            raise InvalidTypeError
        return ScType(self.value | other.value)

    def change_const(self, is_const: bool) -> ScType:
        v = self.value & ~bitmasks.SC_TYPE_CONSTANCY_MASK
        return ScType(v | (bitmasks.SC_TYPE_CONST if is_const else bitmasks.SC_TYPE_VAR))
