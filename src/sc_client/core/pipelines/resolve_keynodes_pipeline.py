from __future__ import annotations

from sc_client import ScAddr, sc_exceptions
from sc_client.constants import common
from sc_client.constants.common import ClientCommand, RequestType
from sc_client.core.pipelines.processing_pipeline import ProcessingPipeline
from sc_client.models import Response, ScIdtfResolveParams
from sc_client.sc_exceptions import ErrorNotes


class ResolveKeynodesPipeline(ProcessingPipeline):
    command_type = ClientCommand.KEYNODES
    request_type = RequestType.KEYNODES

    def __call__(self, *addrs: ScAddr) -> list[ScAddr]:
        payload = self._create_payload(*addrs)
        response = self._sc_connection.send_message(self.request_type, payload)
        self._process_errors(response, payload)
        data = self._response_process(response)
        return data

    @staticmethod
    def _create_payload(*params: ScIdtfResolveParams) -> any:
        if not all(isinstance(par, ScIdtfResolveParams) for par in params):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScIdtfResolveParams")
        payload = []
        for idtf_param in params:
            keynode_type = idtf_param.type
            if keynode_type and keynode_type.is_valid():
                payload_item = {
                    common.COMMAND: common.CommandTypes.RESOLVE,
                    common.IDTF: idtf_param.idtf,
                    common.ELEMENT_TYPE: idtf_param.type.value,
                }
            else:
                payload_item = {
                    common.COMMAND: common.CommandTypes.FIND,
                    common.IDTF: idtf_param.idtf,
                }
            payload.append(payload_item)
        return payload

    @staticmethod
    def _response_process(response: Response) -> list[ScAddr]:
        response_payload = response.payload
        return [ScAddr(addr_value) for addr_value in response_payload]
