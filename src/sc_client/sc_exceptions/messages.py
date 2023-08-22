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


class ErrorNotes:
    """Exception notes that go after default messages"""

    CANNOT_CONNECT_TO_SC_SERVER = "Cannot connect to sc-server"
    CONNECTION_TO_SC_SERVER_LOST = "Connection to sc-server lost"
    SC_SERVER_TAKES_A_LONG_TIME_TO_RESPOND = "Sc-server takes a long time to respond"
    INT_TYPE_INITIALIZATION = "You must use int type for initialization"
    SC_ADDR_OF_IDENTIFIER_IS_INVALID = "ScAddr of {} is invalid"
    EXPECTED_OBJECT_TYPES = "Expected object types: {}"
    EXPECTED_OBJECT_TYPES_SC_ADDR = "Expected object types: ScAddr"
    EXPECTED_SC_TYPE = "Expected ScType: {}"
    ALIAS_MUST_BE_STR = "Alias must be str"
    VALUE_WITH_ALIAS_MUST_BE_SC_ADDR = "Value with alias must be ScAddr"
    VAR_TYPE_IN_TEMPLTE = "You should to use variable types in template"
