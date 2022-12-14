from dataclasses import dataclass
from enum import Enum
from typing import Callable

from sc_client.constants.common import ScEventType
from sc_client.models.sc_addr import ScAddr

ScEventCallbackFunc = Callable[[ScAddr, ScAddr, ScAddr], Enum]


@dataclass
class ScEventParams:
    addr: ScAddr
    event_type: ScEventType
    callback: ScEventCallbackFunc


@dataclass
class ScEvent:
    id: int = 0
    event_type: ScEventType = None
    callback: ScEventCallbackFunc = None
