from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, Tuple, Union

from sc_client.models.sc_addr import ScAddr
from sc_client.models.sc_type import ScType
from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError

ScTemplateValueItem = Union[ScAddr, ScType, str]
ScTemplateAliasedItem = Tuple[Union[ScAddr, ScType], str]
ScTemplateParam = Union[ScTemplateValueItem, ScTemplateAliasedItem]
ScTemplateParams = Dict[str, Union[ScAddr, str]]


class ScTemplateValue:
    value: ScTemplateValueItem
    alias: str | None = None

    def __init__(self, param: ScTemplateParam):
        if isinstance(param, tuple):
            param, alias = param
            if not isinstance(alias, str):
                raise InvalidTypeError(ErrorNotes.ALIAS_MUST_BE_STR)
            if not isinstance(param, (ScAddr, ScType)):
                raise InvalidTypeError(ErrorNotes.VALUE_WITH_ALIAS_MUST_BE_SC_ADDR)
            self.alias = alias
        if isinstance(param, ScType) and param.is_const():
            raise InvalidTypeError(ErrorNotes.VAR_TYPE_IN_TEMPLTE)
        self.value = param


@dataclass
class ScTemplateTriple:
    src: ScTemplateValue
    edge: ScTemplateValue
    trg: ScTemplateValue

    def __init__(self, src: ScTemplateParam, edge: ScTemplateParam, trg: ScTemplateParam) -> None:
        self.src = ScTemplateValue(src)
        self.edge = ScTemplateValue(edge)
        self.trg = ScTemplateValue(trg)


class ScTemplate:
    def __init__(self) -> None:
        self.triple_list: list[ScTemplateTriple] = []

    def triple(
        self,
        src: ScTemplateParam,
        edge: ScTemplateParam,
        trg: ScTemplateParam,
    ) -> ScTemplate:
        self.triple_list.append(ScTemplateTriple(src, edge, trg))
        return self

    def triple_with_relation(
        self,
        src: ScTemplateParam,
        edge: ScTemplateParam,
        trg: ScTemplateParam,
        edge2: ScTemplateParam,
        src2: ScTemplateParam,
    ) -> ScTemplate:
        if not isinstance(edge, tuple):
            edge_alias = f"edge_1_{len(self.triple_list)}"
            edge = (edge, edge_alias)
        self.triple(src, edge, trg)
        self.triple(src2, edge2, edge[1])
        return self


class ScTemplateResult:
    addrs_iter: Iterator[ScAddr]

    def __init__(self, addrs: list[ScAddr], aliases: dict[str, int]) -> None:
        self.addrs = addrs
        self.aliases = aliases

    def __len__(self) -> int:
        return len(self.addrs)

    def get(self, alias_or_index: str | int) -> ScAddr:
        """Get ScAddr by alias or index in the template result"""
        if isinstance(alias_or_index, str):
            return self.addrs[self.aliases[alias_or_index]]
        return self.addrs[alias_or_index]

    def __getitem__(self, index: int) -> ScAddr:
        """Get ScAddr by index in the template result"""
        return self.addrs[index]

    def __iter__(self) -> ScTemplateResult:
        """Iterate by triples"""
        self.addrs_iter = iter(self.addrs)
        return self

    def __next__(self) -> tuple[ScAddr, ScAddr, ScAddr]:
        return next(self.addrs_iter), next(self.addrs_iter), next(self.addrs_iter)
