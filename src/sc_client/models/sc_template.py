import warnings
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple, Union

from sc_client.constants import ScType
from sc_client.constants.exceptions import InvalidTypeError
from sc_client.models.sc_addr import ScAddr
from sc_client.models.sc_event_subscription import ScEventCallbackFunc

ScTemplateValueItem = Union[ScAddr, ScType, str]
ScTemplateAliasedItem = Tuple[Union[ScAddr, ScType], str]
ScTemplateParam = Union[ScTemplateValueItem, ScTemplateAliasedItem]
ScTemplateParams = Dict[str, Union[ScAddr, str]]
ScTemplateIdtf = str


class ScTemplateValue:
    value: ScTemplateValueItem
    alias: Optional[str] = None

    def __init__(self, param: ScTemplateParam):
        if isinstance(param, tuple):
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
    source: ScTemplateValue
    connector: ScTemplateValue
    target: ScTemplateValue

    def __init__(self, source: ScTemplateParam, connector: ScTemplateParam, target: ScTemplateParam):
        self.source = ScTemplateValue(source)
        self.connector = ScTemplateValue(connector)
        self.target = ScTemplateValue(target)


class ScTemplate:
    def __init__(self) -> None:
        self.triple_list: List[ScTemplateTriple] = []

    def triple(
        self,
        source: ScTemplateParam,
        connector: ScTemplateParam,
        target: ScTemplateParam,
    ) -> None:
        self.triple_list.append(ScTemplateTriple(source, connector, target))

    def triple_with_relation(
        self,
        source: ScTemplateParam,
        connector: ScTemplateParam,
        target: ScTemplateParam,
        attribute_connector: ScTemplateParam,
        attribute: ScTemplateParam,
    ) -> None:
        warnings.warn(
            "ScTemplate 'triple_with_relation' method is deprecated. Use `quintuple` method instead.",
            DeprecationWarning,
        )
        self.quintuple(source, connector, target, attribute_connector, attribute)

    def quintuple(
        self,
        source: ScTemplateParam,
        connector: ScTemplateParam,
        target: ScTemplateParam,
        attribute_connector: ScTemplateParam,
        attribute: ScTemplateParam,
    ) -> None:
        if not isinstance(connector, tuple):
            connector_alias = f"connector_1_{len(self.triple_list)}"
            connector = (connector, connector_alias)
        self.triple(source, connector, target)
        self.triple(attribute, attribute_connector, connector[1])


class ScTemplateResult:
    addrs_iter: Iterator[ScAddr]

    def __init__(self, addrs: List[ScAddr], aliases: Dict[str, int]) -> None:
        self.addrs = addrs
        self.aliases = aliases

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

    def __iter__(self):
        """Iterate by triples"""
        self.addrs_iter = iter(self.addrs)
        return self

    def __next__(self) -> Tuple[ScAddr, ScAddr, ScAddr]:
        return next(self.addrs_iter), next(self.addrs_iter), next(self.addrs_iter)
