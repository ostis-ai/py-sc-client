from sc_client import session
from sc_client.client._payload_factory import PayloadFactory
from sc_client.client._resonse_processor import ResponseProcessor
from sc_client.constants.common import ClientCommand, RequestType


class Executor:
    _executor_mapper = {
        ClientCommand.CREATE_ELEMENTS: RequestType.CREATE_ELEMENTS,
        ClientCommand.CREATE_ELEMENTS_BY_SCS: RequestType.CREATE_ELEMENTS_BY_SCS,
        ClientCommand.CHECK_ELEMENTS: RequestType.CHECK_ELEMENTS,
        ClientCommand.DELETE_ELEMENTS: RequestType.DELETE_ELEMENTS,
        ClientCommand.KEYNODES: RequestType.KEYNODES,
        ClientCommand.GET_LINK_CONTENT: RequestType.CONTENT,
        ClientCommand.GET_LINKS_BY_CONTENT: RequestType.CONTENT,
        ClientCommand.GET_LINKS_BY_CONTENT_SUBSTRING: RequestType.CONTENT,
        ClientCommand.SET_LINK_CONTENTS: RequestType.CONTENT,
        ClientCommand.EVENTS_CREATE: RequestType.EVENTS,
        ClientCommand.EVENTS_DESTROY: RequestType.EVENTS,
        ClientCommand.GENERATE_TEMPLATE: RequestType.GENERATE_TEMPLATE,
        ClientCommand.SEARCH_TEMPLATE: RequestType.SEARCH_TEMPLATE,
    }

    def __init__(self):
        self.payload_factory = PayloadFactory()
        self.response_processor = ResponseProcessor()

    def run(self, command_type: ClientCommand, *args):
        payload = self.payload_factory.run(command_type, *args)
        response = session.send_message(self._executor_mapper.get(command_type), payload)
        return self.response_processor.run(command_type, response, *args)
