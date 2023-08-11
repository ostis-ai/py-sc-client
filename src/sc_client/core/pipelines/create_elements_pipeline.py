from __future__ import annotations

from sc_client import ScAddr, ScConstruction, sc_exceptions
from sc_client.constants import common
from sc_client.constants.common import ClientCommand, RequestType
from sc_client.core.pipelines.processing_pipeline import ProcessingPipeline
from sc_client.models import Response
from sc_client.sc_exceptions import ErrorNotes


class CreateElementsPipeline(ProcessingPipeline):
    command_type = ClientCommand.CREATE_ELEMENTS
    request_type = RequestType.CREATE_ELEMENTS

    def __call__(self, constr: ScConstruction) -> list[ScAddr]:
        payload = self._create_payload(constr)
        response = self._sc_connection.send_message(self.request_type, payload)
        self._process_errors(response, payload)
        data = self._response_process(response)
        return data

    @staticmethod
    def _create_payload(constr: ScConstruction) -> any:
        if not isinstance(constr, ScConstruction):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScConstruction")
        payload = []
        for command in constr.commands:
            if command.el_type.is_node():
                payload_part = {
                    common.ELEMENT: common.Elements.NODE,
                    common.TYPE: command.el_type.value,
                }
                payload.append(payload_part)

            elif command.el_type.is_edge():

                def solve_adj(obj: ScAddr | str):
                    if isinstance(obj, ScAddr):
                        return {common.TYPE: common.Types.ADDR, common.VALUE: obj.value}
                    return {
                        common.TYPE: common.Types.REF,
                        common.VALUE: constr.get_index(obj),
                    }

                payload_part = {
                    common.ELEMENT: common.Elements.EDGE,
                    common.TYPE: command.el_type.value,
                    common.SOURCE: solve_adj(command.data.get(common.SOURCE)),
                    common.TARGET: solve_adj(command.data.get(common.TARGET)),
                }
                payload.append(payload_part)

            elif command.el_type.is_link():
                payload_part = {
                    common.ELEMENT: common.Elements.LINK,
                    common.TYPE: command.el_type.value,
                    common.CONTENT: command.data.get(common.CONTENT),
                    common.CONTENT_TYPE: command.data.get(common.TYPE),
                }
                payload.append(payload_part)
        return payload

    @staticmethod
    def _response_process(response: Response) -> list[ScAddr]:
        return [ScAddr(addr_value) for addr_value in response.payload]
