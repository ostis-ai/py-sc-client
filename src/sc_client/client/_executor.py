from sc_client import session
from sc_client.client._payload_factory import PayloadFactory
from sc_client.client._response_processor import ResponseProcessor
from sc_client.constants.common import ERRORS, MESSAGE, REF, ClientCommand, RequestType
from sc_client.constants.exceptions import ServerError


class Executor:
    _executor_mapper = {
        ClientCommand.GENERATE_ELEMENTS: RequestType.GENERATE_ELEMENTS,
        ClientCommand.GENERATE_ELEMENTS_BY_SCS: RequestType.GENERATE_ELEMENTS_BY_SCS,
        ClientCommand.GET_ELEMENTS_TYPES: RequestType.GET_ELEMENTS_TYPES,
        ClientCommand.ERASE_ELEMENTS: RequestType.ERASE_ELEMENTS,
        ClientCommand.SEARCH_KEYNODES: RequestType.SEARCH_KEYNODES,
        ClientCommand.GET_LINK_CONTENT: RequestType.HANDLE_CONTENT,
        ClientCommand.SEARCH_LINKS_BY_CONTENT: RequestType.HANDLE_CONTENT,
        ClientCommand.SEARCH_LINKS_BY_CONTENT_SUBSTRING: RequestType.HANDLE_CONTENT,
        ClientCommand.SEARCH_LINKS_CONTENTS_BY_CONTENT_SUBSTRING: RequestType.HANDLE_CONTENT,
        ClientCommand.SET_LINK_CONTENTS: RequestType.HANDLE_CONTENT,
        ClientCommand.CREATE_EVENT_SUBSCRIPTIONS: RequestType.HANDLE_EVENT_SUBSCRIPTIONS,
        ClientCommand.DESTROY_EVENT_SUBSCRIPTIONS: RequestType.HANDLE_EVENT_SUBSCRIPTIONS,
        ClientCommand.GENERATE_BY_TEMPLATE: RequestType.GENERATE_BY_TEMPLATE,
        ClientCommand.SEARCH_BY_TEMPLATE: RequestType.SEARCH_BY_TEMPLATE,
    }

    def __init__(self):
        self.payload_factory = PayloadFactory()
        self.response_processor = ResponseProcessor()

    def run(self, command_type: ClientCommand, *args):
        payload = self.payload_factory.run(command_type, *args)
        response = session.send_message(self._executor_mapper.get(command_type), payload)
        if response.get(ERRORS):
            error_msgs = []
            errors = response.get(ERRORS)
            if isinstance(errors, str):
                error_msgs.append(errors)
            else:
                for error in errors:
                    payload_part = "\nPayload: " + str(payload[int(error.get(REF))]) if error.get(REF) else ""
                    error_msgs.append(error.get(MESSAGE) + payload_part)
            error_msgs = "\n".join(error_msgs)
            raise ServerError(error_msgs)
        return self.response_processor.run(command_type, response, *args)
