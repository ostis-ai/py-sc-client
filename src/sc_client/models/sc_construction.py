from __future__ import annotations

import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Any, TypedDict, Union

from sc_client.constants import ScType, common
from sc_client.constants.exceptions import InvalidTypeError, LinkContentOversizeError
from sc_client.constants.numeric import LINK_CONTENT_MAX_SIZE
from sc_client.models.sc_addr import ScAddr


class ScConstruction:
    def __init__(self) -> None:
        self.aliases = {}
        self.commands = []

    def create_node(self, sc_type: ScType, alias: str = None) -> None:
        if not sc_type.is_node():
            raise InvalidTypeError("You should pass the node type here")
        cmd = ScConstructionCommand(sc_type, None)
        if alias:
            self.aliases[alias] = len(self.commands)
        self.commands.append(cmd)

    def create_edge(
        self,
        sc_type: ScType,
        src: str | ScAddr,
        trg: str | ScAddr,
        alias: str = None,
    ) -> None:
        if not sc_type.is_edge():
            raise InvalidTypeError("You should pass the edge type here")
        cmd = ScConstructionCommand(sc_type, {common.SOURCE: src, common.TARGET: trg})
        if alias:
            self.aliases[alias] = len(self.commands)
        self.commands.append(cmd)

    def create_link(self, sc_type: ScType, content: ScLinkContent, alias: str = None) -> None:
        if not sc_type.is_link():
            raise InvalidTypeError("You should pass the link type here")
        cmd = ScConstructionCommand(sc_type, {common.CONTENT: content.data, common.TYPE: content.content_type.value})
        if alias:
            self.aliases[alias] = len(self.commands)
        self.commands.append(cmd)

    def get_index(self, alias: str) -> int:
        return self.aliases[alias]


@dataclass
class ScConstructionCommand:
    el_type: ScType
    data: Any


class ScIdtfResolveParams(TypedDict):
    idtf: str
    type: ScType | None


class ScLinkContentType(Enum):
    INT = 0
    FLOAT = 1
    STRING = 2


ScLinkContentData = Union[str, int, float]


@dataclass
class ScLinkContent:
    data: ScLinkContentData
    content_type: ScLinkContentType
    addr: ScAddr = None

    def __post_init__(self):
        if len(str(self.data)) > LINK_CONTENT_MAX_SIZE:
            raise LinkContentOversizeError
        if isinstance(self.content_type, int):
            warnings.warn(
                "ScLinkContentType in ScLinkContent int is deprecated. Use enum type instead", DeprecationWarning
            )
            # TODO: remove check int in version 0.3.0
            self.content_type = ScLinkContentType(self.content_type)

    def type_to_str(self) -> str:
        return self.content_type.name.lower()


class Response(TypedDict):
    id: int
    status: bool
    event: bool
    payload: Any
