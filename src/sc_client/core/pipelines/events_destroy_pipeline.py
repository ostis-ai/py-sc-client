from __future__ import annotations

from sc_client import ScEvent, ScEventParams, sc_exceptions
from sc_client.constants import common
from sc_client.constants.common import ClientCommand, RequestType
from sc_client.core.pipelines.processing_pipeline import ProcessingPipeline
from sc_client.models import Response
from sc_client.sc_exceptions import ErrorNotes


class EventsDestroyPipeline(ProcessingPipeline):
    command_type = ClientCommand.EVENTS_DESTROY
    request_type = RequestType.EVENTS

    def __call__(self, *events: ScEventParams) -> bool:
        payload = self._create_payload(*events)
        response = self._sc_connection.send_message(self.request_type, payload)
        self._process_errors(response, payload)
        data = self._response_process(response, *events)
        return data

    @staticmethod
    def _create_payload(*events: ScEvent) -> any:
        if not all(isinstance(event, ScEvent) for event in events):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScEvent")
        return {common.CommandTypes.DELETE: [event.id for event in events]}

    def _response_process(self, response: Response, *events: ScEvent) -> bool:
        for event in events:
            self._sc_connection.drop_event(event.id)
        return response.status
