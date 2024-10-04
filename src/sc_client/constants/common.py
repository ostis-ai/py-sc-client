"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from enum import Enum, auto


class RequestType(Enum):
    GET_ELEMENTS_TYPES = "check_elements"
    GENERATE_ELEMENTS = "create_elements"
    GENERATE_ELEMENTS_BY_SCS = "create_elements_by_scs"
    ERASE_ELEMENTS = "delete_elements"
    HANDLE_CONTENT = "content"
    SEARCH_KEYNODES = "keynodes"
    SEARCH_BY_TEMPLATE = "search_template"
    GENERATE_BY_TEMPLATE = "generate_template"
    HANDLE_EVENT_SUBSCRIPTIONS = "events"


class ClientCommand(Enum):
    GET_ELEMENTS_TYPES = auto()
    GENERATE_ELEMENTS = auto()
    GENERATE_ELEMENTS_BY_SCS = auto()
    ERASE_ELEMENTS = auto()
    SET_LINK_CONTENTS = auto()
    GET_LINK_CONTENT = auto()
    SEARCH_LINKS_BY_CONTENT = auto()
    SEARCH_LINKS_BY_CONTENT_SUBSTRING = auto()
    SEARCH_LINKS_CONTENTS_BY_CONTENT_SUBSTRING = auto()
    SEARCH_KEYNODES = auto()
    SEARCH_BY_TEMPLATE = auto()
    GENERATE_BY_TEMPLATE = auto()
    CREATE_EVENT_SUBSCRIPTIONS = auto()
    DESTROY_EVENT_SUBSCRIPTIONS = auto()


SOURCE = "src"
CONNECTOR = "edge"
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


class Elements:
    NODE = "node"
    CONNECTOR = "edge"
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
    SEARCH = "find"
    SEARCH_LINKS_BY_CONTENT_SUBSTRING = "find_links_by_substr"
    SEARCH_LINKS_CONTENTS_BY_CONTENT_SUBSTRING = "find_strings_by_substr"
    GENERATE = "create"
    ERASE = "delete"


ELEMENT_TYPE = "elType"
IDTF = "idtf"
TEMPLATE = "templ"
PARAMS = "params"
IS_REQUIRED = "is_required"


class ScEventType(Enum):
    UNKNOWN = "unknown"
    AFTER_GENERATE_CONNECTOR = "sc_event_after_generate_connector"
    AFTER_GENERATE_OUTGOING_ARC = "sc_event_after_generate_outgoing_arc"
    AFTER_GENERATE_INCOMING_ARC = "sc_event_after_generate_incoming_arc"
    AFTER_GENERATE_EDGE = "sc_event_after_generate_edge"
    BEFORE_ERASE_CONNECTOR = "sc_event_before_erase_connector"
    BEFORE_ERASE_OUTGOING_ARC = "sc_event_before_erase_outgoing_arc"
    BEFORE_ERASE_INCOMING_ARC = "sc_event_before_erase_incoming_arc"
    BEFORE_ERASE_EDGE = "sc_event_before_erase_edge"
    BEFORE_ERASE_ELEMENT = "sc_event_before_erase_element"
    BEFORE_CHANGE_LINK_CONTENT = "sc_event_before_change_link_content"
