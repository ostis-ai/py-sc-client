from __future__ import annotations

from sc_client import ScAddr, ScLinkContent, ScLinkContentType, sc_exceptions
from sc_client.constants import common
from sc_client.constants.common import ClientCommand, RequestType
from sc_client.core.pipelines.processing_pipeline import ProcessingPipeline
from sc_client.models import Response, ScLinkContentData
from sc_client.sc_exceptions import ErrorNotes


class GetLinksByContentPipeline(ProcessingPipeline):
    command_type = ClientCommand.GET_LINKS_BY_CONTENT
    request_type = RequestType.CONTENT

    def __call__(self, *contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
        payload = self._create_payload(*contents)
        response = self._sc_connection.send_message(self.request_type, payload)
        self._process_errors(response, payload)
        data = self._response_process(response)
        return data

    def _create_payload(self, *contents: ScLinkContent | ScLinkContentData) -> any:
        if not all(isinstance(content, (ScLinkContent, str, int, float)) for content in contents):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScLinkContent, str, int or float")
        link_contents = []
        for content in contents:
            if isinstance(content, ScLinkContent):
                link_contents.append(content)
            elif isinstance(content, str):
                link_contents.append(ScLinkContent(content, ScLinkContentType.STRING))
            elif isinstance(content, int):
                link_contents.append(ScLinkContent(content, ScLinkContentType.INT))
            else:  # float
                link_contents.append(ScLinkContent(content, ScLinkContentType.FLOAT))
        return [self._form_payload_content(content) for content in link_contents]

    @staticmethod
    def _form_payload_content(content):
        return {
            common.COMMAND: common.CommandTypes.FIND,
            common.DATA: content.data,
        }

    @staticmethod
    def _response_process(response: Response) -> list[list[ScAddr]]:
        response_payload = response.payload
        if response_payload:
            return [[ScAddr(addr_value) for addr_value in addr_list] for addr_list in response_payload]
        return response_payload
