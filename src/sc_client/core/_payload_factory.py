from __future__ import annotations

import abc
import re
from typing import get_origin

from sc_client import sc_exceptions
from sc_client.constants import common
from sc_client.models import (
    ScAddr,
    ScConstruction,
    ScEvent,
    ScEventParams,
    ScIdtfResolveParams,
    ScLinkContent,
    ScLinkContentType,
    SCs,
    SCsText,
    ScTemplate,
    ScTemplateParams,
    ScTemplateValue,
    ScType,
)
from sc_client.models.sc_construction import ScLinkContentData
from sc_client.sc_exceptions import ErrorNotes


class BasePayloadCreator(abc.ABC):
    @abc.abstractmethod
    def __call__(self, *args) -> any:
        pass


class CreateElementsPayloadCreator(BasePayloadCreator):
    def __call__(self, constr: ScConstruction, *_) -> any:
        if not isinstance(constr, ScConstruction):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScConstruction")
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
    def __call__(self, scs_text: SCsText, *_) -> any:
        if not isinstance(scs_text, list) or any(isinstance(n, (str, SCs)) for n in scs_text):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "string or SCs")
        return [
            {
                common.SCS: scs,
                common.OUTPUT_STRUCTURE: 0,
            }
            if isinstance(scs, str)
            else {
                common.SCS: scs.text,
                common.OUTPUT_STRUCTURE: scs.output_struct.value,
            }
            for scs in scs_text
        ]


class CheckElementsPayloadCreator(BasePayloadCreator):
    def __call__(self, *addrs: ScAddr) -> any:
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        return [addr.value for addr in addrs]


class DeleteElementsPayloadCreator(BasePayloadCreator):
    def __call__(self, *addrs: ScAddr) -> any:
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        return [addr.value for addr in addrs]


class SetLinkContentPayloadCreator(BasePayloadCreator):
    def __call__(self, *contents: ScLinkContent) -> any:
        if not all(isinstance(content, ScLinkContent) for content in contents):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        return [
            {
                common.COMMAND: common.CommandTypes.SET,
                common.TYPE: content.type_to_str(),
                common.DATA: content.data,
                common.ADDR: content.addr.value,
            }
            for content in contents
        ]


class GetLinkContentPayloadCreator(BasePayloadCreator):
    def __call__(self, *addrs: ScAddr) -> any:
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        return [
            {
                common.COMMAND: common.CommandTypes.GET,
                common.ADDR: addr.value,
            }
            for addr in addrs
        ]


class GetLinksByContentPayloadCreator(BasePayloadCreator):
    def __call__(self, *contents: ScLinkContent | ScLinkContentData) -> any:
        if not all(isinstance(content, (ScLinkContent, str, int, float)) for content in contents):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScLinkContent, str, int or float")
        link_contents = []
        for content in contents:
            if isinstance(content, ScLinkContent):
                link_contents.append(content)
            elif isinstance(content, str):
                link_contents.append(ScLinkContent(content, ScLinkContentType.STRING))
            elif isinstance(content, int):
                link_contents.append(ScLinkContent(content, ScLinkContentType.INT))
            else:  # float
                link_contents.append(ScLinkContent(content, ScLinkContentType.FLOAT))
        return [self._form_payload_content(content) for content in link_contents]

    @staticmethod
    def _form_payload_content(content):
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
    def __call__(self, *params: ScIdtfResolveParams) -> any:
        if not all(isinstance(par, ScIdtfResolveParams) for par in params):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScIdtfResolveParams")
        payload = []
        for idtf_param in params:
            keynode_type = idtf_param.type
            if keynode_type and keynode_type.is_valid():
                payload_item = {
                    common.COMMAND: common.CommandTypes.RESOLVE,
                    common.IDTF: idtf_param.idtf,
                    common.ELEMENT_TYPE: idtf_param.type.value,
                }
            else:
                payload_item = {
                    common.COMMAND: common.CommandTypes.FIND,
                    common.IDTF: idtf_param.idtf,
                }
            payload.append(payload_item)
        return payload


class TemplatePayloadCreator(BasePayloadCreator):
    def __call__(
        self,
        template: ScTemplate | str | ScAddr,
        params: ScTemplateParams,
        *_,
    ) -> any:
        if not isinstance(template, (ScTemplate, str, ScAddr)):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScTemplate, str or ScArrd")
        if isinstance(template, ScAddr):
            payload_template = {
                common.TYPE: common.Types.ADDR,
                common.VALUE: template.value,
            }
        elif isinstance(template, str) and re.match("^([a-z]|\\d|_)+", template):
            payload_template = {common.TYPE: common.Types.IDTF, common.VALUE: template}
        elif isinstance(template, str):
            payload_template = template
        else:
            payload_template = self._process_template(template)

        payload_params = {}
        if params is not None:
            if not isinstance(params, get_origin(ScTemplateParams)):
                raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScTemplateParams")
            for alias, addr in params.items():
                if isinstance(addr, ScAddr):
                    payload_params.update({alias: addr.value})
                else:
                    payload_params.update({alias: str(addr)})
        return {common.TEMPLATE: payload_template, common.PARAMS: payload_params}

    @classmethod
    def _process_template(cls, template: ScTemplate):
        payload_template = []
        for triple in template.triple_list:
            items = [triple.src, triple.edge, triple.trg]
            payload_template.append([cls._process_triple_item(item) for item in items])
        return payload_template

    @staticmethod
    def _process_triple_item(item: ScTemplateValue) -> dict:
        if isinstance(item.value, ScAddr):
            result = {common.TYPE: common.Types.ADDR, common.VALUE: item.value.value}
        elif isinstance(item.value, ScType):
            result = {common.TYPE: common.Types.TYPE, common.VALUE: item.value.value}
        else:
            result = {common.TYPE: common.Types.ALIAS, common.VALUE: item.value}
        if item.alias:
            result[common.ALIAS] = item.alias
        return result


class EventsCreatePayloadCreator(BasePayloadCreator):
    def __call__(self, *events: ScEventParams) -> any:
        if not all(isinstance(event, ScEventParams) for event in events):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScEventParams")
        payload_create = [{common.TYPE: event.event_type.value, common.ADDR: event.addr.value} for event in events]
        return {common.CommandTypes.CREATE: payload_create}


class EventsDestroyPayloadCreator(BasePayloadCreator):
    def __call__(self, *events: ScEvent) -> any:
        if not all(isinstance(event, ScEvent) for event in events):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScEvent")
        return {common.CommandTypes.DELETE: [event.id for event in events]}


class PayloadFactory:
    def __init__(self) -> None:
        self._payload_request_mapper: dict[common.ClientCommand, BasePayloadCreator] = {
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

    def run(self, request_type: common.ClientCommand, *args) -> any:
        return self._payload_request_mapper.get(request_type)(*args)
