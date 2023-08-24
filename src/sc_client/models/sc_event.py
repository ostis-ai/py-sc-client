from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Optional

from sc_client.constants.common import ScEventType
from sc_client.models.sc_addr import ScAddr

ScEventCallback = Callable[[ScAddr, ScAddr, ScAddr], None]
AsyncScEventCallback = Callable[[ScAddr, ScAddr, ScAddr], Coroutine[Any, Any, None]]


@dataclass
class ScEventParams:
    addr: ScAddr
    event_type: ScEventType
    callback: ScEventCallback


@dataclass
class ScEvent:
    id: int
    event_type: Optional[ScEventType] = None
    callback: Optional[ScEventCallback] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, event_type={self.event_type})"


@dataclass
class AsyncScEventParams:
    addr: ScAddr
    event_type: ScEventType
    callback: AsyncScEventCallback


@dataclass
class AsyncScEvent:
    id: int
    event_type: Optional[ScEventType] = None
    callback: Optional[AsyncScEventCallback] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, event_type={self.event_type})"
