import warnings
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple, Union

from sc_client.constants import ScType
from sc_client.constants.exceptions import InvalidTypeError
from sc_client.models.sc_addr import ScAddr
from sc_client.models.sc_event import ScEventCallbackFunc

ScTemplateValueItem = Union[ScAddr, ScType, str]
ScTemplateAliasedItem = Tuple[Union[ScAddr, ScType], str]
ScTemplateAliasedItemDeprecated = List[Union[ScAddr, ScType, str]]  # TODO: remove list support in version 0.3.0
ScTemplateParam = Union[ScTemplateValueItem, ScTemplateAliasedItem, ScTemplateAliasedItemDeprecated]
ScTemplateParams = Dict[str, Union[ScAddr, str]]
ScTemplateIdtf = str


class ScTemplateValue:
    value: ScTemplateValueItem
    alias: Optional[str] = None

    def __init__(self, param: ScTemplateParam):
        if isinstance(param, (tuple, list)):
            if isinstance(param, list):
                warnings.warn(
                    "ScTemplateParam with type 'list' param is deprecated. Use 'tuple' or '>>' instead",
                    DeprecationWarning,
                )
                # TODO: remove list checking in version 0.3.0
            param, alias = param
            if not isinstance(alias, str):
                raise InvalidTypeError("Alias must be str")
            if not isinstance(param, (ScAddr, ScType)):
                raise InvalidTypeError("Value with alias must be ScAddr")
            self.alias = alias
        if isinstance(param, ScType) and param.is_const():
            raise InvalidTypeError("You should to use variable types in template")
        self.value = param


@dataclass
class ScTemplateTriple:
    src: ScTemplateValue
    edge: ScTemplateValue
    trg: ScTemplateValue

    def __init__(self, src: ScTemplateParam, edge: ScTemplateParam, trg: ScTemplateParam):
        self.src = ScTemplateValue(src)
        self.edge = ScTemplateValue(edge)
        self.trg = ScTemplateValue(trg)


class ScTemplate:
    def __init__(self) -> None:
        self.triple_list: List[ScTemplateTriple] = []

    def triple(
        self,
        src: ScTemplateParam,
        edge: ScTemplateParam,
        trg: ScTemplateParam,
    ) -> None:
        self.triple_list.append(ScTemplateTriple(src, edge, trg))

    def triple_with_relation(
        self,
        src: ScTemplateParam,
        edge: ScTemplateParam,
        trg: ScTemplateParam,
        edge2: ScTemplateParam,
        src2: ScTemplateParam,
    ) -> None:
        if not isinstance(edge, (tuple, list)):  # TODO: remove list support in version 0.3.0
            edge_alias = f"edge_1_{len(self.triple_list)}"
            edge = (edge, edge_alias)
        self.triple(src, edge, trg)
        self.triple(src2, edge2, edge[1])


class ScTemplateResult:
    addrs_iter: Iterator[ScAddr]

    def __init__(self, addrs: List[ScAddr], aliases: Dict[str, int]) -> None:
        self.addrs = addrs
        self.aliases = aliases

    def size(self) -> int:
        warnings.warn("ScTemplateResult 'size()' method is deprecated. Use 'len(res)' instead", DeprecationWarning)
        # TODO: remove method in version 0.3.0
        return len(self)

    def __len__(self) -> int:
        return len(self.addrs)

    def get(self, alias_or_index: Union[str, int]) -> ScAddr:
        """Get ScAddr by alias or index in template result"""
        if isinstance(alias_or_index, str):
            return self.addrs[self.aliases[alias_or_index]]
        return self.addrs[alias_or_index]

    def __getitem__(self, index: int) -> ScAddr:
        """Get ScAddr by index in template result"""
        return self.addrs[index]

    def for_each_triple(self, func: ScEventCallbackFunc):
        warnings.warn(
            "ScTemplateResult 'for_each_triple()' method is deprecated. Use for-iteration instead.",
            DeprecationWarning,
        )
        # TODO: remove method in version 0.3.0
        for i in range(0, len(self), 3):
            func(self.addrs[i], self.addrs[i + 1], self.addrs[i + 2])

    def __iter__(self):
        """Iterate by triples"""
        self.addrs_iter = iter(self.addrs)
        return self

    def __next__(self) -> Tuple[ScAddr, ScAddr, ScAddr]:
        return next(self.addrs_iter), next(self.addrs_iter), next(self.addrs_iter)
