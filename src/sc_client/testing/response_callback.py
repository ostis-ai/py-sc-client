import abc
import asyncio
import json
from typing import Any, Dict

from sc_client.constants import common
from sc_client.models import Response


class ResponseCallback(abc.ABC):
    def __init__(self, delay: float = 0.0) -> None:
        self.delay = delay
        self.call_times: int = 0

    @abc.abstractmethod
    def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
        pass

    async def process_response(self, message_json: str) -> str:
        await asyncio.sleep(self.delay)
        self.call_times += 1
        message: Dict[str, any] = json.loads(message_json)
        try:
            response = self.callback(
                message[common.ID],
                common.RequestType(message[common.TYPE]),
                message[common.PAYLOAD],
            )
        except AssertionError as e:
            response = Response(message[common.ID], False, False, None, str(e))
        return response.dump()
