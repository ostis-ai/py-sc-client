from __future__ import annotations

import re
from typing import get_args, get_origin

from sc_client._internal_utils import process_triple_item
from sc_client.constants import common, exceptions
from sc_client.models import (
    ScAddr,
    ScConstruction,
    ScEvent,
    ScEventParams,
    ScIdtfResolveParams,
    ScLinkContent,
    ScLinkContentType,
    SCsText,
    ScTemplate,
    ScTemplateIdtf,
    ScTemplateParams,
)


class BasePayloadCreator:
    def __init__(self):
        pass

    def __call__(self, *args):
        raise NotImplementedError


class CreateElementsPayloadCreator(BasePayloadCreator):
    def __call__(self, constr: ScConstruction, *_):
        if not isinstance(constr, ScConstruction):
            raise exceptions.InvalidTypeError("expected object types: ScConstruction")
        payload = []
        for command in constr.commands:
            if command.el_type.is_node():
                payload_part = {
                    common.ELEMENT: common.Elements.NODE,
                    common.TYPE: command.el_type.value,
                }
                payload.append(payload_part)

            elif command.el_type.is_edge():

                def solve_adj(obj: ScAddr | str):
                    if isinstance(obj, ScAddr):
                        return {common.TYPE: common.Types.ADDR, common.VALUE: obj.value}
                    return {
                        common.TYPE: common.Types.REF,
                        common.VALUE: constr.get_index(obj),
                    }

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
        return payload


class CreateElementsBySCsPayloadCreator(BasePayloadCreator):
    def __call__(self, scs: SCsText, *_):
        if not isinstance(scs, get_origin(SCsText)) or not all(isinstance(n, get_args(SCsText)) for n in scs):
            raise exceptions.InvalidTypeError("expected object types: List[str]")
        return scs


class CheckElementsPayloadCreator(BasePayloadCreator):
    def __call__(self, *addrs: ScAddr):
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise exceptions.InvalidTypeError("expected object types: ScAddr")
        return [addr.value for addr in addrs]


class DeleteElementsPayloadCreator(BasePayloadCreator):
    def __call__(self, *addrs: ScAddr):
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise exceptions.InvalidTypeError("expected object types: ScAddr")
        return [addr.value for addr in addrs]


class SetLinkContentPayloadCreator(BasePayloadCreator):
    def __call__(self, *contents: ScLinkContent):
        if not all(isinstance(content, ScLinkContent) for content in contents):
            raise exceptions.InvalidTypeError("expected object types: ScAddr")
        payload = [
            {
                common.COMMAND: common.CommandTypes.SET,
                common.TYPE: content.type_to_str(),
                common.DATA: content.data,
                common.ADDR: content.addr.value,
            }
            for content in contents
        ]
        return payload


class GetLinkContentPayloadCreator(BasePayloadCreator):
    def __call__(self, *addrs: ScAddr):
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise exceptions.InvalidTypeError("expected object types: ScAddr")
        payload = [
            {
                common.COMMAND: common.CommandTypes.GET,
                common.ADDR: addr.value,
            }
            for addr in addrs
        ]
        return payload


class GetLinksByContentPayloadCreator(BasePayloadCreator):
    def __call__(self, *contents: ScLinkContent | str | int):
        if not all(isinstance(content, (ScLinkContent, str, int)) for content in contents):
            raise exceptions.InvalidTypeError("expected object types: ScLinkContent, str or int")
        link_contents = []
        for content in contents:
            if isinstance(content, str):
                link_contents.append(ScLinkContent(content, ScLinkContentType.STRING))
            elif isinstance(content, int):
                link_contents.append(ScLinkContent(content, ScLinkContentType.INT))
            else:
                link_contents.append(content)
        payload = []
        for content in link_contents:
            payload.append(self._form_payload_content(content))
        return payload

    def _form_payload_content(self, content):
        return {
            common.COMMAND: common.CommandTypes.FIND,
            common.DATA: content.data,
        }


class GetLinksByContentSubstringPayloadCreator(GetLinksByContentPayloadCreator):
    def _form_payload_content(self, content):
        return {
            common.COMMAND: common.CommandTypes.FIND_LINKS_BY_SUBSTRING,
            common.DATA: content.data,
        }


class GetLinksContentsByContentSubstringPayloadCreator(GetLinksByContentPayloadCreator):
    def _form_payload_content(self, content):
        return {
            common.COMMAND: common.CommandTypes.FIND_LINKS_CONTENTS_BY_CONTENT_SUBSTRING,
            common.DATA: content.data,
        }


class ResolveKeynodesPayloadCreator(BasePayloadCreator):
    def __call__(self, *params: ScIdtfResolveParams):
        if not all(isinstance(par, dict) for par in params):
            raise exceptions.InvalidTypeError("expected object types: ScIdtfResolveParams")
        payload = []
        for idtf_param in params:
            keynode_type = idtf_param.get(common.TYPE)
            if keynode_type and keynode_type.is_valid():
                payload_item = {
                    common.COMMAND: common.CommandTypes.RESOLVE,
                    common.IDTF: idtf_param.get(common.IDTF),
                    common.ELEMENT_TYPE: idtf_param.get(common.TYPE).value,
                }
            else:
                payload_item = {
                    common.COMMAND: common.CommandTypes.FIND,
                    common.IDTF: idtf_param.get(common.IDTF),
                }
            payload.append(payload_item)
        return payload


class TemplatePayloadCreator(BasePayloadCreator):
    def __call__(self, template: ScTemplate | str | ScTemplateIdtf | ScAddr, params: ScTemplateParams, *_):
        if not isinstance(template, (ScTemplate, str, ScTemplateIdtf, ScAddr)):
            raise exceptions.InvalidTypeError("expected object types: ScTemplate | str | ScTemplateIdtf")
        if isinstance(template, ScAddr):
            payload_template = {common.TYPE: common.Types.ADDR, common.VALUE: template.value}
        elif isinstance(template, str) and re.match("^([a-z]|\\d|_)+", template):
            payload_template = {common.TYPE: common.Types.IDTF, common.VALUE: template}
        elif isinstance(template, str):
            payload_template = template
        else:
            payload_template = self._process_template(template)

        payload_params = {}
        if params is not None:
            if not isinstance(params, get_origin(ScTemplateParams)):
                raise exceptions.InvalidTypeError("expected object types: ScTemplateParams")
            for alias, addr in params.items():
                if isinstance(addr, ScAddr):
                    payload_params.update({alias: addr.value})
                else:
                    payload_params.update({alias: str(addr)})
        return {common.TEMPLATE: payload_template, common.PARAMS: payload_params}

    def _process_template(self, template: ScTemplate):
        payload_template = []
        for triple in template.triple_list:
            items = [
                triple.get(common.SOURCE),
                triple.get(common.EDGE),
                triple.get(common.TARGET),
            ]
            payload_template.append([process_triple_item(item) for item in items])
        return payload_template


class EventsCreatePayloadCreator(BasePayloadCreator):
    def __call__(self, *events: ScEventParams):
        if not all(isinstance(event, ScEventParams) for event in events):
            raise exceptions.InvalidTypeError("expected object types: ScEventParams")
        payload_create = [{common.TYPE: event.event_type.value, common.ADDR: event.addr.value} for event in events]
        payload = {common.CommandTypes.CREATE: payload_create}
        return payload


class EventsDestroyPayloadCreator(BasePayloadCreator):
    def __call__(self, *events: ScEvent):
        if not all(isinstance(event, ScEvent) for event in events):
            raise exceptions.InvalidTypeError("expected object types: ScEvent")
        payload = {common.CommandTypes.DELETE: [event.id for event in events]}
        return payload


class PayloadFactory:
    _payload_request_mapper = {
        common.ClientCommand.CREATE_ELEMENTS: CreateElementsPayloadCreator(),
        common.ClientCommand.CREATE_ELEMENTS_BY_SCS: CreateElementsBySCsPayloadCreator(),
        common.ClientCommand.CHECK_ELEMENTS: CheckElementsPayloadCreator(),
        common.ClientCommand.DELETE_ELEMENTS: DeleteElementsPayloadCreator(),
        common.ClientCommand.KEYNODES: ResolveKeynodesPayloadCreator(),
        common.ClientCommand.GET_LINK_CONTENT: GetLinkContentPayloadCreator(),
        common.ClientCommand.GET_LINKS_BY_CONTENT: GetLinksByContentPayloadCreator(),
        common.ClientCommand.GET_LINKS_BY_CONTENT_SUBSTRING: GetLinksByContentSubstringPayloadCreator(),
        common.ClientCommand.GET_LINKS_CONTENTS_BY_CONTENT_SUBSTRING: GetLinksByContentSubstringPayloadCreator(),
        common.ClientCommand.SET_LINK_CONTENTS: SetLinkContentPayloadCreator(),
        common.ClientCommand.EVENTS_CREATE: EventsCreatePayloadCreator(),
        common.ClientCommand.EVENTS_DESTROY: EventsDestroyPayloadCreator(),
        common.ClientCommand.GENERATE_TEMPLATE: TemplatePayloadCreator(),
        common.ClientCommand.SEARCH_TEMPLATE: TemplatePayloadCreator(),
    }

    def run(self, request_type: common.ClientCommand, *args, **kwargs):
        _creator = self._payload_request_mapper.get(request_type)
        return _creator(*args, **kwargs)
