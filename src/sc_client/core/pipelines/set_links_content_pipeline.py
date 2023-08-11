from __future__ import annotations

from sc_client import ScLinkContent, sc_exceptions
from sc_client.constants import common
from sc_client.constants.common import ClientCommand, RequestType
from sc_client.core.pipelines.processing_pipeline import ProcessingPipeline
from sc_client.models import Response
from sc_client.sc_exceptions import ErrorNotes


class SetLinksContentPipeline(ProcessingPipeline):
    command_type = ClientCommand.SET_LINK_CONTENTS
    request_type = RequestType.CONTENT

    def __call__(self, *contents: ScLinkContent) -> bool:
        payload = self._create_payload(*contents)
        response = self._sc_connection.send_message(self.request_type, payload)
        self._process_errors(response, payload)
        data = self._response_process(response)
        return data

    @staticmethod
    def _create_payload(*contents: ScLinkContent) -> any:
        if not all(isinstance(content, ScLinkContent) for content in contents):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        return [
            {
                common.COMMAND: common.CommandTypes.SET,
                common.TYPE: content.type_to_str(),
                common.DATA: content.data,
                common.ADDR: content.addr.value,
            }
            for content in contents
        ]

    @staticmethod
    def _response_process(response: Response) -> bool:
        return response.status
