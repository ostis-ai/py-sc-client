"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
"""

from __future__ import annotations

from typing import List, Union

from sc_client import session
from sc_client.constants import common
from sc_client.constants.sc_types import ScType
from sc_client.models import (
    ScAddr,
    ScConstruction,
    ScEvent,
    ScEventParams,
    ScIdtfResolveParams,
    ScLinkContent,
    ScLinkContentType,
    ScTemplate,
    ScTemplateGenParams,
    ScTemplateResult,
)
from sc_client._internal_utils import process_triple_item


def connect(url: str) -> None:
    session.set_connection(url)


def is_connected() -> bool:
    return session.is_connection_established()


def disconnect() -> None:
    session.close_connection()


def check_elements(addrs: List[ScAddr]) -> List[ScType]:
    if not addrs:
        return []
    addr_values = [addr.value for addr in addrs]
    response = session.send_message(common.RequestTypes.CHECK_ELEMENTS, addr_values)
    return [ScType(type_value) for type_value in response.get(common.PAYLOAD)]


def create_elements(constr: ScConstruction) -> List[ScAddr]:
    payload = []
    for command in constr.commands:
        if command.el_type.is_node():
            payload_part = {
                common.ELEMENT: common.Elements.NODE,
                common.TYPE: command.el_type.value
            }
            payload.append(payload_part)

        elif command.el_type.is_edge():

            def solve_adj(obj: Union[ScAddr, str]):
                if isinstance(obj, ScAddr):
                    return {common.TYPE: common.Types.ADDR, common.VALUE: obj.value}
                return {common.TYPE: common.Types.REF, common.VALUE: constr.get_index(obj)}

            payload_part = {
                common.ELEMENT: common.Elements.EDGE,
                common.TYPE: command.el_type.value,
                common.SOURCE: solve_adj(command.data.get(common.SOURCE)),
                common.TARGET: solve_adj(command.data.get(common.TARGET)),
            }
            payload.append(payload_part)

        elif command.el_type.is_link():
            payload_part = {
                common.ELEMENT: common.Elements.LINK,
                common.TYPE: command.el_type.value,
                common.CONTENT: command.data.get(common.CONTENT),
                common.CONTENT_TYPE: command.data.get(common.TYPE),
            }
            payload.append(payload_part)
    response = session.send_message(common.RequestTypes.CREATE_ELEMENTS, payload)
    return [ScAddr(addr_value) for addr_value in response.get(common.PAYLOAD)]


def delete_elements(addrs: List[ScAddr]) -> bool:
    addr_values = [addr.value for addr in addrs]
    response = session.send_message(common.RequestTypes.DELETE_ELEMENTS, addr_values)
    return response.get(common.STATUS)


def set_link_contents(contents: List[ScLinkContent]) -> bool:
    payload = [
        {
            common.COMMAND: common.CommandTypes.SET,
            common.TYPE: content.type_to_str(),
            common.DATA: content.data,
            common.ADDR: content.addr.value,
        }
        for content in contents
    ]
    response = session.send_message(common.RequestTypes.CONTENT, payload)
    return response.get(common.STATUS)


def get_link_content(addr: ScAddr) -> ScLinkContent:
    payload = {
        common.COMMAND: common.CommandTypes.GET,
        common.ADDR: addr.value,
    }
    response = session.send_message(common.RequestTypes.CONTENT, [payload])
    response_payload = response.get(common.PAYLOAD)[0]
    str_type = response_payload.get(common.TYPE)
    content_type = 0
    if str_type == common.STRING:
        content_type = ScLinkContentType.STRING.value
    elif str_type == common.INT:
        content_type = ScLinkContentType.INT.value
    elif str_type == common.BINARY:
        content_type = ScLinkContentType.BINARY.value
    elif str_type == common.FLOAT:
        content_type = ScLinkContentType.FLOAT.value
    return ScLinkContent(response_payload.get(common.VALUE), content_type, addr)


def get_link_by_content(contents: List[ScLinkContent | str | int]) -> List[List[ScAddr]]:
    link_contents = []
    for content in contents:
        if isinstance(content, str):
            link_contents.append(ScLinkContent(content, ScLinkContentType.STRING.value))
        else:
            link_contents.append(content)
    payload = [
        {
            common.COMMAND: common.CommandTypes.FIND,
            common.DATA: content.data,
        }
        for content in link_contents
    ]
    response = session.send_message(common.RequestTypes.CONTENT, payload)
    response_payload = response.get(common.PAYLOAD)
    if response_payload:
        return [[ScAddr(addr_value) for addr_value in addr_list] for addr_list in response_payload]
    return response_payload


def resolve_keynodes(params: List[ScIdtfResolveParams]) -> List[ScAddr]:
    payloads_list = []
    for idtf_param in params:
        keynode_type = idtf_param.get(common.TYPE)
        if keynode_type and keynode_type.is_valid():
            payload = {
                common.COMMAND: common.CommandTypes.RESOLVE,
                common.IDTF: idtf_param.get(common.IDTF),
                common.ELEMENT_TYPE: idtf_param.get(common.TYPE).value,
            }
        else:
            payload = {
                common.COMMAND: common.CommandTypes.FIND,
                common.IDTF: idtf_param.get(common.IDTF),
            }
        payloads_list.append(payload)
    response = session.send_message(common.RequestTypes.KEYNODES, payloads_list)
    response_payload = response.get(common.PAYLOAD)
    if response_payload:
        return [ScAddr(addr_value) for addr_value in response_payload]
    return response_payload


def template_search(template: Union[ScTemplate, str]) -> List[ScTemplateResult]:
    payload = []
    if isinstance(template, str):
        payload = template
    else:
        for triple in template.triple_list:
            items = [triple.get(common.SOURCE), triple.get(common.EDGE), triple.get(common.TARGET)]
            payload_triple = [process_triple_item(item) for item in items]
            is_required = triple.get(common.IS_REQUIRED)
            if not is_required:
                payload_triple.append({common.IS_REQUIRED: is_required})
            payload.append(payload_triple)

    response = session.send_message(common.RequestTypes.SEARCH_TEMPLATE, payload)
    result = []
    if response.get(common.STATUS):
        response_payload = response.get(common.PAYLOAD)
        aliases = response_payload.get(common.ALIASES)
        all_addrs = response_payload.get(common.ADDRS)
        for addrs_list in all_addrs:
            addrs = [ScAddr(addr) for addr in addrs_list]
            result.append(ScTemplateResult(addrs, aliases))
    return result


def template_generate(template: Union[ScTemplate, str], params: ScTemplateGenParams) -> ScTemplateResult:
    payload_template = []
    if isinstance(template, str):
        payload_template = template
    else:
        for triple in template.triple_list:
            items = [triple.get(common.SOURCE), triple.get(common.EDGE), triple.get(common.TARGET)]
            payload_template.append([process_triple_item(item) for item in items])
    payload_params = {alias: addr.value for alias, addr in params.items()}
    payload = {common.TEMPLATE: payload_template, common.PARAMS: payload_params}
    response = session.send_message(common.RequestTypes.GENERATE_TEMPLATE, payload)
    result = None
    if response.get(common.STATUS):
        response_payload = response.get(common.PAYLOAD)
        aliases = response_payload.get(common.ALIASES)
        addrs_list = response_payload.get(common.ADDRS)
        addrs = [ScAddr(addr) for addr in addrs_list]
        result = ScTemplateResult(addrs, aliases)
    return result


def events_create(events: List[ScEventParams]) -> List[ScEvent]:
    payload_create = [{common.TYPE: event.event_type.value, common.ADDR: event.addr.value} for event in events]
    payload = {common.CommandTypes.CREATE: payload_create}
    response = session.send_message(common.RequestTypes.EVENTS, payload)
    result = []
    for count, event in enumerate(events):
        command_id = response.get(common.PAYLOAD)[count]
        sc_event = ScEvent(command_id, event.event_type, event.callback)
        session.set_event(sc_event)
        result.append(sc_event)
    return result


def events_destroy(events: List[ScEvent]) -> bool:
    payload = {common.CommandTypes.DELETE: [event.id for event in events]}
    response = session.send_message(common.RequestTypes.EVENTS, payload)
    for event in events:
        session.drop_event(event.id)
    return response.get(common.STATUS)


def is_event_valid(event: ScEvent) -> bool:
    return bool(session.get_event(event.id))
