from enum import Enum


class RequestTypes:
    CHECK_ELEMENTS = "check_elements"
    CREATE_ELEMENTS = "create_elements"
    DELETE_ELEMENTS = "delete_elements"
    CONTENT = "content"
    KEYNODES = "keynodes"
    SEARCH_TEMPLATE = "search_template"
    GENERATE_TEMPLATE = "generate_template"
    EVENTS = "events"


BINARY = "binary"
INT = "int"
FLOAT = "float"
STRING = "string"

SOURCE = "src"
EDGE = "edge"
TARGET = "trg"

ID = "id"
ADDR = "addr"
ADDRS = "addrs"
VALUE = "value"
ALIAS = "alias"
ALIASES = "aliases"
CONTENT = "content"
CONTENT_TYPE = "content_type"
PAYLOAD = "payload"
STATUS = "status"
EVENT = "event"
DATA = "data"

ELEMENT = "el"


class Elements:
    NODE = "node"
    EDGE = "edge"
    LINK = "link"


TYPE = "type"


class Types:
    ADDR = "addr"
    TYPE = "type"
    ALIAS = "alias"
    REF = "ref"


COMMAND = "command"


class CommandTypes:
    SET = "set"
    GET = "get"
    RESOLVE = "resolve"
    FIND = "find"
    CREATE = "create"
    DELETE = "delete"


ELEMENT_TYPE = "elType"
IDTF = "idtf"
TEMPLATE = "templ"
PARAMS = "params"
IS_REQUIRED = "is_required"


class ScEventType(Enum):
    UNKNOWN = "unknown"
    ADD_OUTGOING_EDGE = "add_outgoing_edge"
    ADD_INGOING_EDGE = "add_ingoing_edge"
    REMOVE_OUTGOING_EDGE = "remove_outgoing_edge"
    REMOVE_INGOING_EDGE = "remove_ingoing_edge"
    REMOVE_ELEMENT = "delete_element"
    CHANGE_CONTENT = "content_change"
