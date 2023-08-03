from __future__ import annotations

from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError


class ScAddr:
    def __init__(self, value: int = 0) -> None:
        if not isinstance(value, int):
            raise InvalidTypeError(ErrorNotes.INT_TYPE_INITIALIZATION)
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def __hash__(self) -> int:
        return hash((self.value, self.__class__))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def __rshift__(self, alias: str) -> tuple[ScAddr, str]:
        return self, alias

    def __eq__(self, other: ScAddr) -> bool:
        if not isinstance(other, ScAddr):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        return self.value == other.value

    def is_equal(self, other: ScAddr) -> bool:
        return self.__eq__(other)

    def __bool__(self) -> bool:
        return self.value != 0

    def is_valid(self) -> bool:
        return self.__bool__()

    def __lt__(self, other: ScAddr) -> bool:
        return self.value < other.value
