from __future__ import annotations

from sc_client import ScAddr, ScType, sc_exceptions
from sc_client.constants.common import ClientCommand, RequestType
from sc_client.core.pipelines.processing_pipeline import ProcessingPipeline
from sc_client.models import Response
from sc_client.sc_exceptions import ErrorNotes


class CheckElementsPipeline(ProcessingPipeline):
    command_type = ClientCommand.CHECK_ELEMENTS
    request_type = RequestType.CHECK_ELEMENTS

    def __call__(self, *addrs: ScAddr) -> list[ScType]:
        payload = self._create_payload(*addrs)
        response = self._sc_connection.send_message(self.request_type, payload)
        self._process_errors(response, payload)
        data = self._response_process(response)
        return data

    @staticmethod
    def _create_payload(*addrs: ScAddr) -> any:
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        return [addr.value for addr in addrs]

    @staticmethod
    def _response_process(response: Response) -> list[ScType]:
        return [ScType(type_value) for type_value in response.payload]
