from dataclasses import dataclass
from typing import List, Union, Dict

from sc_client.constants import ScType
from sc_client.constants.exceptions import InvalidTypeError, InvalidValueError
from sc_client.models.sc_addr import ScAddr
from sc_client.models.sc_event import ScEventCallbackFunc

ScTemplateValueItem = Union[ScAddr, ScType, str]
ScTemplateParam = Union[ScTemplateValueItem, List[ScTemplateValueItem]]
ScTemplateParams = Dict[str, Union[ScAddr, str]]
ScTemplateIdtf = str


@dataclass
class ScTemplateValue:
    value: ScTemplateValueItem
    alias: Union[str, None] = None


@dataclass
class ScTemplateTriple:
    src: ScTemplateValue
    edge: ScTemplateValue
    trg: ScTemplateValue


class ScTemplate:
    def __init__(self) -> None:
        self.triple_list: List[ScTemplateTriple] = []

    def triple(
            self,
            src: ScTemplateParam,
            edge: ScTemplateParam,
            trg: ScTemplateParam,
    ) -> None:
        for param in (src, edge, trg):
            if isinstance(param, List):
                self._is_var_type(param[0])
            else:
                self._is_var_type(param)
        p1, p2, p3 = tuple(map(self._split_template_param, [src, edge, trg]))

        self.triple_list.append(ScTemplateTriple(src=p1, edge=p2, trg=p3))

    @staticmethod
    def _is_var_type(param: ScTemplateParam):
        if isinstance(param, ScType) and param.is_const():
            raise InvalidTypeError("You should to use variable types in template")

    def triple_with_relation(
            self,
            src: ScTemplateParam,
            edge: ScTemplateParam,
            trg: ScTemplateParam,
            edge2: ScTemplateParam,
            src2: ScTemplateParam,
    ) -> None:
        template_value = self._split_template_param(edge)
        alias = template_value.alias
        value = template_value.value
        if not alias:
            alias = f"edge_1_{len(self.triple_list)}"
        self.triple(src, [value, alias], trg)
        self.triple(src2, edge2, alias)

    @staticmethod
    def _split_template_param(param: ScTemplateParam) -> ScTemplateValue:
        if isinstance(param, list):
            if len(param) != 2:
                raise InvalidValueError("Invalid number of values for replacement. Use [ScType | ScAddr, string]")
            value, alias = param
            if not isinstance(value, (ScAddr, ScType)) or not isinstance(alias, str):
                raise InvalidTypeError("The first parameter should be ScAddr or ScType. The second one is a string")
            return ScTemplateValue(value=value, alias=alias)
        return ScTemplateValue(value=param, alias=None)


class ScTemplateResult:
    def __init__(self, addrs: List[ScAddr], aliases: List[str]) -> None:
        self.addrs = addrs
        self.indecies = aliases

    def size(self) -> int:
        return len(self.addrs)

    def get(self, alias_or_index: Union[str, int]) -> ScAddr:
        if isinstance(alias_or_index, str):
            return self.addrs[self.indecies[alias_or_index]]
        return self.addrs[alias_or_index]

    def for_each_triple(self, func: ScEventCallbackFunc):
        for i in range(0, self.size(), 3):
            func(self.addrs[i], self.addrs[i + 1], self.addrs[i + 2])
