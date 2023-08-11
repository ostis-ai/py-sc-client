from __future__ import annotations

from sc_client import SCs, sc_exceptions
from sc_client.constants import common
from sc_client.constants.common import ClientCommand, RequestType
from sc_client.core.pipelines.processing_pipeline import ProcessingPipeline
from sc_client.models import Response, SCsText
from sc_client.sc_exceptions import ErrorNotes


class CreateElementsBySCsPipeline(ProcessingPipeline):
    command_type = ClientCommand.CREATE_ELEMENTS_BY_SCS
    request_type = RequestType.CREATE_ELEMENTS_BY_SCS

    def __call__(self, scs_text: SCsText) -> list[bool]:
        payload = self._create_payload(scs_text)
        response = self._sc_connection.send_message(self.request_type, payload)
        self._process_errors(response, payload)
        data = self._response_process(response)
        return data

    @staticmethod
    def _create_payload(scs_text: SCsText) -> any:
        if not isinstance(scs_text, list) or any(isinstance(n, (str, SCs)) for n in scs_text):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "string or SCs")
        return [
            {
                common.SCS: scs,
                common.OUTPUT_STRUCTURE: 0,
            }
            if isinstance(scs, str)
            else {
                common.SCS: scs.text,
                common.OUTPUT_STRUCTURE: scs.output_struct.value,
            }
            for scs in scs_text
        ]

    @staticmethod
    def _response_process(response: Response) -> list[bool]:
        return [bool(result) for result in response.payload]
