from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Optional

from sc_client.constants.common import ScEventType
from sc_client.models.sc_addr import ScAddr

AScEventCallback = Callable[[ScAddr, ScAddr, ScAddr], Coroutine[Any, Any, None]]


@dataclass
class AScEventParams:
    addr: ScAddr
    event_type: ScEventType
    callback: AScEventCallback


@dataclass
class AScEvent:
    id: int
    event_type: Optional[ScEventType] = None
    callback: Optional[AScEventCallback] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, event_type={self.event_type})"
