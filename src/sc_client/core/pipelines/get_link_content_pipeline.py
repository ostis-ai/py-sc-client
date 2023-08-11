from __future__ import annotations

from sc_client import ScAddr, ScLinkContent, ScLinkContentType, sc_exceptions
from sc_client.constants import common
from sc_client.constants.common import TYPE, VALUE, ClientCommand, RequestType
from sc_client.core.pipelines.processing_pipeline import ProcessingPipeline
from sc_client.models import Response
from sc_client.sc_exceptions import ErrorNotes


class GetLinkContentPipeline(ProcessingPipeline):
    command_type = ClientCommand.GET_LINK_CONTENT
    request_type = RequestType.CONTENT

    def __call__(self, *addrs: ScAddr) -> list[ScLinkContent]:
        payload = self._create_payload(*addrs)
        response = self._sc_connection.send_message(self.request_type, payload)
        self._process_errors(response, payload)
        data = self._response_process(response)
        return data

    @staticmethod
    def _create_payload(*addrs: ScAddr) -> any:
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        return [
            {
                common.COMMAND: common.CommandTypes.GET,
                common.ADDR: addr.value,
            }
            for addr in addrs
        ]

    @staticmethod
    def _response_process(response: Response) -> list[ScLinkContent]:
        response_payload = response.payload
        result = []
        for link in response_payload:
            str_type: str = link.get(TYPE)
            result.append(ScLinkContent(link.get(VALUE), ScLinkContentType[str_type.upper()]))
        return result
