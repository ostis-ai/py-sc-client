from enum import Enum, IntEnum, auto


class RequestType(Enum):
    CHECK_ELEMENTS = "check_elements"
    CREATE_ELEMENTS = "create_elements"
    CREATE_ELEMENTS_BY_SCS = "create_elements_by_scs"
    DELETE_ELEMENTS = "delete_elements"
    CONTENT = "content"
    KEYNODES = "keynodes"
    SEARCH_TEMPLATE = "search_template"
    GENERATE_TEMPLATE = "generate_template"
    EVENTS = "events"


class ClientCommand(IntEnum):
    CHECK_ELEMENTS = auto()
    CREATE_ELEMENTS = auto()
    CREATE_ELEMENTS_BY_SCS = auto()
    DELETE_ELEMENTS = auto()
    SET_LINK_CONTENTS = auto()
    GET_LINK_CONTENT = auto()
    GET_LINKS_BY_CONTENT = auto()
    GET_LINKS_BY_CONTENT_SUBSTRING = auto()
    GET_LINKS_CONTENTS_BY_CONTENT_SUBSTRING = auto()
    KEYNODES = auto()
    SEARCH_TEMPLATE = auto()
    GENERATE_TEMPLATE = auto()
    EVENTS_CREATE = auto()
    EVENTS_DESTROY = auto()


class Elements:
    NODE = "node"
    EDGE = "edge"
    LINK = "link"


class Types:
    ADDR = "addr"
    TYPE = "type"
    ALIAS = "alias"
    REF = "ref"
    IDTF = "idtf"


class CommandTypes:
    SET = "set"
    GET = "get"
    RESOLVE = "resolve"
    FIND = "find"
    FIND_LINKS_BY_SUBSTRING = "find_links_by_substr"
    FIND_LINKS_CONTENTS_BY_CONTENT_SUBSTRING = "find_strings_by_substr"
    CREATE = "create"
    DELETE = "delete"


class ScEventType(Enum):
    UNKNOWN = "unknown"
    ADD_OUTGOING_EDGE = "add_outgoing_edge"
    ADD_INGOING_EDGE = "add_ingoing_edge"
    REMOVE_OUTGOING_EDGE = "remove_outgoing_edge"
    REMOVE_INGOING_EDGE = "remove_ingoing_edge"
    REMOVE_ELEMENT = "delete_element"
    CHANGE_CONTENT = "content_change"


SOURCE = "src"
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
ERRORS = "errors"
MESSAGE = "message"
REF = "ref"
DATA = "data"
ELEMENT = "el"
SCS = "scs"
OUTPUT_STRUCTURE = "output_structure"
TYPE = "type"
COMMAND = "command"
ELEMENT_TYPE = "elType"
IDTF = "idtf"
TEMPLATE = "templ"
PARAMS = "params"
