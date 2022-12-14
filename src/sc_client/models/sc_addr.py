from __future__ import annotations

from sc_client.constants.exceptions import InvalidTypeError


class ScAddr:
    def __init__(self, value: int = 0) -> None:
        if not isinstance(value, int):
            raise InvalidTypeError("You should to use int type for ScAddr initialization")
        self.value = value

    def __hash__(self) -> int:
        return hash((self.value, self.__class__))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def __rshift__(self, alias: str) -> tuple[ScAddr, str]:
        return self, alias

    def __eq__(self, other: ScAddr) -> bool:
        if not isinstance(other, ScAddr):
            raise InvalidTypeError(f"Cannot compare ScAddr with {type(other)}")
        return self.value == other.value

    def __bool__(self) -> bool:
        return self.value != 0

    def is_equal(self, other: ScAddr) -> bool:
        return self.__eq__(other)

    def is_valid(self) -> bool:
        return self.__bool__()
