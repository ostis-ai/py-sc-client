import abc
import json
from typing import Any, Dict

from sc_client.constants import common
from sc_client.core.response import Response


class ResponseCallback(abc.ABC):
    def __init__(self, delay: float = 0.0) -> None:
        self.delay = delay
        self.call_times: int = 0

    @abc.abstractmethod
    def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
        pass

    async def process_response(self, message_json: str) -> str:
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


class SimpleResponseCallback(ResponseCallback):
    def __init__(self, status: bool, event: bool, payload: any, errors: any, delay: float = 0.0) -> None:
        super().__init__(delay)
        self.status = status
        self.event = event
        self.payload = payload
        self.errors = errors

    def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
        return Response(id_, self.status, self.event, self.payload, self.errors)
