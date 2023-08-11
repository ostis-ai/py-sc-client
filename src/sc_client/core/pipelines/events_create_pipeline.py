from __future__ import annotations

from sc_client import ScEvent, ScEventParams, sc_exceptions
from sc_client.constants import common
from sc_client.constants.common import ClientCommand, RequestType
from sc_client.core.pipelines.processing_pipeline import ProcessingPipeline
from sc_client.models import Response
from sc_client.sc_exceptions import ErrorNotes


class EventsCreatePipeline(ProcessingPipeline):
    command_type = ClientCommand.EVENTS_CREATE
    request_type = RequestType.EVENTS

    def __call__(self, *events: ScEventParams) -> list[ScEvent]:
        payload = self._create_payload(*events)
        response = self._sc_connection.send_message(self.request_type, payload)
        self._process_errors(response, payload)
        data = self._response_process(response, *events)
        return data

    @staticmethod
    def _create_payload(*events: ScEventParams) -> any:
        if not all(isinstance(event, ScEventParams) for event in events):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScEventParams")
        payload_create = [{common.TYPE: event.event_type.value, common.ADDR: event.addr.value} for event in events]
        return {common.CommandTypes.CREATE: payload_create}

    def _response_process(self, response: Response, *events: ScEvent) -> list[ScEvent]:
        result = []
        for count, event in enumerate(events):
            command_id = response.payload[count]
            sc_event = ScEvent(command_id, event.event_type, event.callback)
            self._sc_connection.set_event(sc_event)
            result.append(sc_event)
        return result
