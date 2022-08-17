"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from enum import Enum, auto


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


class ClientCommand(Enum):
    CHECK_ELEMENTS = auto()
    CREATE_ELEMENTS = auto()
    CREATE_ELEMENTS_BY_SCS = auto()
    DELETE_ELEMENTS = auto()
    SET_LINK_CONTENTS = auto()
    GET_LINK_CONTENT = auto()
    GET_LINKS_BY_CONTENT = auto()
    GET_LINKS_BY_CONTENT_SUBSTRING = auto()
    KEYNODES = auto()
    SEARCH_TEMPLATE = auto()
    GENERATE_TEMPLATE = auto()
    EVENTS_CREATE = auto()
    EVENTS_DESTROY = auto()


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
    IDTF = "idtf"


COMMAND = "command"


class CommandTypes:
    SET = "set"
    GET = "get"
    RESOLVE = "resolve"
    FIND = "find"
    FIND_BY_SUBSTRING = "find_by_substr"
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
