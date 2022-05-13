from __future__ import annotations

from sc_client._internal_utils import process_triple_item
from sc_client.constants import common
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
)


class BasePayloadCreator:
    def __init__(self):
        pass

    def __call__(self, *args):
        raise NotImplementedError


class CreateElementsPayloadCreator(BasePayloadCreator):
    def __call__(self, constr: ScConstruction, *_):
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


class CheckElementsPayloadCreator(BasePayloadCreator):
    def __call__(self, *addrs: ScAddr):
        return [addr.value for addr in addrs]


class DeleteElementsPayloadCreator(BasePayloadCreator):
    def __call__(self, *addrs: ScAddr):
        return [addr.value for addr in addrs]


class SetLinkContentPayloadCreator(BasePayloadCreator):
    def __call__(self, *contents: ScLinkContent):
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
    def __call__(self, addr: ScAddr, *_):
        payload = {
            common.COMMAND: common.CommandTypes.GET,
            common.ADDR: addr.value,
        }
        return payload


class GetLinksByContentPayloadCreator(BasePayloadCreator):
    def __call__(self, *contents: ScLinkContent | str | int):
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
        return payload


class ResolveKeynodesPayloadCreator(BasePayloadCreator):
    def __call__(self, *params: ScIdtfResolveParams):
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


class TemplateSearchPayloadCreator(BasePayloadCreator):
    def __call__(self, template: ScTemplate | str, *_):
        payload = []
        if isinstance(template, str):
            payload = template
        else:
            for triple in template.triple_list:
                items = [
                    triple.get(common.SOURCE),
                    triple.get(common.EDGE),
                    triple.get(common.TARGET),
                ]
                payload_triple = [process_triple_item(item) for item in items]
                is_required = triple.get(common.IS_REQUIRED)
                if not is_required:
                    payload_triple.append({common.IS_REQUIRED: is_required})
                payload.append(payload_triple)
        return payload


class TemplateGeneratePayloadCreator(BasePayloadCreator):
    def __call__(self, template: ScTemplate | str, params: ScTemplateGenParams, *_):
        payload_template = []
        if isinstance(template, str):
            payload_template = template
        else:
            for triple in template.triple_list:
                items = [
                    triple.get(common.SOURCE),
                    triple.get(common.EDGE),
                    triple.get(common.TARGET),
                ]
                payload_template.append([process_triple_item(item) for item in items])
        payload_params = {alias: addr.value for alias, addr in params.items()}
        payload = {common.TEMPLATE: payload_template, common.PARAMS: payload_params}
        return payload


class EventsCreatePayloadCreator(BasePayloadCreator):
    def __call__(self, *events: ScEventParams):
        payload_create = [{common.TYPE: event.event_type.value, common.ADDR: event.addr.value} for event in events]
        payload = {common.CommandTypes.CREATE: payload_create}
        return payload


class EventsDestroyPayloadCreator(BasePayloadCreator):
    def __call__(self, *events: ScEvent):
        payload = {common.CommandTypes.DELETE: [event.id for event in events]}
        return payload


class PayloadFactory:
    _payload_request_mapper = {
        common.ClientCommand.CREATE_ELEMENTS: CreateElementsPayloadCreator(),
        common.ClientCommand.CHECK_ELEMENTS: CheckElementsPayloadCreator(),
        common.ClientCommand.DELETE_ELEMENTS: DeleteElementsPayloadCreator(),
        common.ClientCommand.KEYNODES: ResolveKeynodesPayloadCreator(),
        common.ClientCommand.GET_LINK_CONTENT: GetLinkContentPayloadCreator(),
        common.ClientCommand.GET_LINKS_BY_CONTENT: GetLinksByContentPayloadCreator(),
        common.ClientCommand.SET_LINK_CONTENTS: SetLinkContentPayloadCreator(),
        common.ClientCommand.EVENTS_CREATE: EventsCreatePayloadCreator(),
        common.ClientCommand.EVENTS_DESTROY: EventsDestroyPayloadCreator(),
        common.ClientCommand.GENERATE_TEMPLATE: TemplateGeneratePayloadCreator(),
        common.ClientCommand.SEARCH_TEMPLATE: TemplateSearchPayloadCreator(),
    }

    def run(self, request_type: common.ClientCommand, *args, **kwargs):
        _creator = self._payload_request_mapper.get(request_type)
        return _creator(*args, **kwargs)
