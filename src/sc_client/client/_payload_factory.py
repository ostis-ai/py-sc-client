from __future__ import annotations

import re
from typing import get_origin

from sc_client._internal_utils import process_triple_item
from sc_client.constants import common, exceptions
from sc_client.models import (
    ScAddr,
    ScConstruction,
    ScEventSubscription,
    ScEventSubscriptionParams,
    ScIdtfResolveParams,
    ScLinkContent,
    ScLinkContentType,
    SCs,
    SCsText,
    ScTemplate,
    ScTemplateIdtf,
    ScTemplateParams,
)
from sc_client.models.sc_construction import ScLinkContentData


class BasePayloadCreator:
    def __init__(self):
        pass

    def __call__(self, *args):
        raise NotImplementedError


class GenerateElementsPayloadCreator(BasePayloadCreator):
    def __call__(self, constr: ScConstruction, *_):
        if not isinstance(constr, ScConstruction):
            raise exceptions.InvalidTypeError("expected object types: ScConstruction")
        payload = []
        for command in constr.commands:
            if command.el_type.is_link():
                payload_part = {
                    common.ELEMENT: common.Elements.LINK,
                    common.TYPE: command.el_type.value,
                    common.CONTENT: command.data.get(common.CONTENT),
                    common.CONTENT_TYPE: command.data.get(common.TYPE),
                }
                payload.append(payload_part)

            elif command.el_type.is_node():
                payload_part = {
                    common.ELEMENT: common.Elements.NODE,
                    common.TYPE: command.el_type.value,
                }
                payload.append(payload_part)

            elif command.el_type.is_connector():

                def solve_adj(obj: ScAddr | str):
                    if isinstance(obj, ScAddr):
                        return {common.TYPE: common.Types.ADDR, common.VALUE: obj.value}
                    return {
                        common.TYPE: common.Types.REF,
                        common.VALUE: constr.get_index(obj),
                    }

                payload_part = {
                    common.ELEMENT: common.Elements.CONNECTOR,
                    common.TYPE: command.el_type.value,
                    common.SOURCE: solve_adj(command.data.get(common.SOURCE)),
                    common.TARGET: solve_adj(command.data.get(common.TARGET)),
                }
                payload.append(payload_part)
        return payload


class GenerateElementsBySCsPayloadCreator(BasePayloadCreator):
    def __call__(self, scs_text: SCsText, *_):
        if not isinstance(scs_text, list) or not all(isinstance(n, (str, SCs)) for n in scs_text):
            raise exceptions.InvalidTypeError("expected object types: string or SCs(string, ScAddr)")
        payload = []
        for scs in scs_text:
            if isinstance(scs, str):
                payload.append(
                    {
                        common.SCS: scs,
                        common.OUTPUT_STRUCTURE: 0,
                    }
                )
            else:
                payload.append(
                    {
                        common.SCS: scs.text,
                        common.OUTPUT_STRUCTURE: scs.output_struct.value,
                    }
                )

        return payload


class GetElementsTypesPayloadCreator(BasePayloadCreator):
    def __call__(self, *addrs: ScAddr):
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise exceptions.InvalidTypeError("expected object types: ScAddr")
        return [addr.value for addr in addrs]


class EraseElementsPayloadCreator(BasePayloadCreator):
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


class SearchLinksByContentPayloadCreator(BasePayloadCreator):
    def __call__(self, *contents: ScLinkContent | ScLinkContentData):
        if not all(isinstance(content, (ScLinkContent, str, int, float)) for content in contents):
            raise exceptions.InvalidTypeError("expected object types: ScLinkContent, str or int")
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

        payload = []
        for content in link_contents:
            payload.append(self._form_payload_content(content))
        return payload

    def _form_payload_content(self, content):
        return {
            common.COMMAND: common.CommandTypes.SEARCH,
            common.DATA: content.data,
        }


class SearchLinksByContentSubstringPayloadCreator(SearchLinksByContentPayloadCreator):
    def _form_payload_content(self, content):
        return {
            common.COMMAND: common.CommandTypes.SEARCH_LINKS_BY_CONTENT_SUBSTRING,
            common.DATA: content.data,
        }


class SearchLinksContentsByContentSubstringPayloadCreator(SearchLinksByContentPayloadCreator):
    def _form_payload_content(self, content):
        return {
            common.COMMAND: common.CommandTypes.SEARCH_LINKS_CONTENTS_BY_CONTENT_SUBSTRING,
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
                    common.COMMAND: common.CommandTypes.SEARCH,
                    common.IDTF: idtf_param.get(common.IDTF),
                }
            payload.append(payload_item)
        return payload


class TemplatePayloadCreator(BasePayloadCreator):
    def __call__(
        self,
        template: ScTemplate | str | ScTemplateIdtf | ScAddr,
        params: ScTemplateParams,
        *_,
    ):
        if not isinstance(template, (ScTemplate, str, ScTemplateIdtf, ScAddr)):
            raise exceptions.InvalidTypeError("expected object types: ScTemplate | str | ScTemplateIdtf")
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
            items = [triple.source, triple.connector, triple.target]
            payload_template.append([process_triple_item(item) for item in items])
        return payload_template


class CreateEventSubscriptionsPayloadCreator(BasePayloadCreator):
    def __call__(self, *event_subscription_params: ScEventSubscriptionParams):
        if not all(isinstance(params, ScEventSubscriptionParams) for params in event_subscription_params):
            raise exceptions.InvalidTypeError("expected object types: ScEventSubscriptionParams")
        payload_generate = [
            {common.TYPE: params.event_type.value, common.ADDR: params.addr.value}
            for params in event_subscription_params
        ]
        payload = {common.CommandTypes.GENERATE: payload_generate}
        return payload


class DestroyEventSubscriptionsPayloadCreator(BasePayloadCreator):
    def __call__(self, *event_subscription_params: ScEventSubscription):
        if not all(isinstance(params, ScEventSubscription) for params in event_subscription_params):
            raise exceptions.InvalidTypeError("expected object types: ScEventSubscription")
        payload = {common.CommandTypes.ERASE: [params.id for params in event_subscription_params]}
        return payload


class PayloadFactory:
    _payload_request_mapper = {
        common.ClientCommand.GENERATE_ELEMENTS: GenerateElementsPayloadCreator(),
        common.ClientCommand.GENERATE_ELEMENTS_BY_SCS: GenerateElementsBySCsPayloadCreator(),
        common.ClientCommand.GET_ELEMENTS_TYPES: GetElementsTypesPayloadCreator(),
        common.ClientCommand.ERASE_ELEMENTS: EraseElementsPayloadCreator(),
        common.ClientCommand.SEARCH_KEYNODES: ResolveKeynodesPayloadCreator(),
        common.ClientCommand.SET_LINK_CONTENTS: SetLinkContentPayloadCreator(),
        common.ClientCommand.GET_LINK_CONTENT: GetLinkContentPayloadCreator(),
        common.ClientCommand.SEARCH_LINKS_BY_CONTENT: SearchLinksByContentPayloadCreator(),
        common.ClientCommand.SEARCH_LINKS_BY_CONTENT_SUBSTRING: SearchLinksByContentSubstringPayloadCreator(),
        common.ClientCommand.SEARCH_LINKS_CONTENTS_BY_CONTENT_SUBSTRING: SearchLinksContentsByContentSubstringPayloadCreator(),
        common.ClientCommand.CREATE_EVENT_SUBSCRIPTIONS: CreateEventSubscriptionsPayloadCreator(),
        common.ClientCommand.DESTROY_EVENT_SUBSCRIPTIONS: DestroyEventSubscriptionsPayloadCreator(),
        common.ClientCommand.GENERATE_BY_TEMPLATE: TemplatePayloadCreator(),
        common.ClientCommand.SEARCH_BY_TEMPLATE: TemplatePayloadCreator(),
    }

    def run(self, request_type: common.ClientCommand, *args, **kwargs):
        _creator = self._payload_request_mapper.get(request_type)
        return _creator(*args, **kwargs)
