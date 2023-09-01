class ErrorDefaultMessages:
    """Common description of exceptions"""

    CANNOT_CONNECT_TO_SC_SERVER = "Cannot connect to sc-server"
    INVALID_STATE = "Invalid state"
    INVALID_VALUE = "Invalid value"
    INVALID_TYPE = "Invalid type"
    MERGE_ERROR = "You can't merge two different syntax types"
    LINK_OVERSIZE = "Link content exceeds permitted value"
    SC_SERVER_ERROR = "Sc-server error"
    PAYLOAD_MAX_SIZE = "Payload max size error"
    EVENT_ERROR = "ScEvent error"


class ErrorNotes:
    """Exception notes that go after default messages"""

    CANNOT_CONNECT_TO_SC_SERVER = "Cannot connect to sc-server"
    CONNECTION_TO_SC_SERVER_LOST = "Connection to sc-server lost"
    SC_SERVER_TAKES_A_LONG_TIME_TO_RESPOND = "Sc-server takes a long time to respond"
    ALREADY_DISCONNECTED = "You already disconnected from the sc-server before"
    INT_TYPE_INITIALIZATION = "You must use int type for initialization"
    SC_ADDR_OF_IDENTIFIER_IS_INVALID = "ScAddr of {} is invalid"
    EXPECTED_OBJECT_TYPES = "Expected object types: {}"
    EXPECTED_OBJECT_TYPES_SC_ADDR = "Expected object types: ScAddr"
    EXPECTED_SC_TYPE = "Expected ScType: {}"
    ALIAS_MUST_BE_STR = "Alias must be str"
    VALUE_WITH_ALIAS_MUST_BE_SC_ADDR = "Value with alias must be ScAddr"
    VAR_TYPE_IN_TEMPLATE = "You should to use variable types in template"
    EVENT_IS_NOT_FOUND = "Event id={} is not found or was dropped"
    GOT_ERROR = "Got error from sc-server: \n{}"
