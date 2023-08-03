from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Union

from sc_client.constants import common
from sc_client.constants.common import ERRORS, EVENT, ID, PAYLOAD, STATUS
from sc_client.constants.config import LINK_CONTENT_MAX_SIZE
from sc_client.models import ScAddr
from sc_client.models.sc_type import ScType
from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError, LinkContentOversizeError


class ScConstruction:
    def __init__(self) -> None:
        self.aliases: dict[str, int] = {}
        self.commands: list[ScConstructionCommand] = []

    def create_node(self, sc_type: ScType, alias: str = None) -> None:
        if not sc_type.is_node():
            raise InvalidTypeError(ErrorNotes.EXPECTED_SC_TYPE, "node")
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
            raise InvalidTypeError(ErrorNotes.EXPECTED_SC_TYPE, "edge")
        cmd = ScConstructionCommand(sc_type, {common.SOURCE: src, common.TARGET: trg})
        if alias:
            self.aliases[alias] = len(self.commands)
        self.commands.append(cmd)

    def create_link(self, sc_type: ScType, content: ScLinkContent, alias: str = None) -> None:
        if not sc_type.is_link():
            raise InvalidTypeError(ErrorNotes.EXPECTED_SC_TYPE, "link")
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


@dataclass
class ScIdtfResolveParams:
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

    def type_to_str(self) -> str:
        return self.content_type.name.lower()


@dataclass
class Response:
    id: int
    status: bool
    event: bool
    payload: Any
    errors: Any

    @classmethod
    def load(cls, response: str) -> Response:
        response: dict = json.loads(response)
        instance = cls(
            id=response.get(ID),
            status=response.get(STATUS),
            event=response.get(EVENT),
            payload=response.get(PAYLOAD),
            errors=response.get(ERRORS),
        )
        return instance
