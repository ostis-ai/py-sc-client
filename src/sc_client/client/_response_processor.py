from __future__ import annotations

from sc_client import session
from sc_client.constants import common as c
from sc_client.constants.sc_types import ScType
from sc_client.models import Response, ScAddr, ScEvent, ScLinkContent, ScLinkContentType, ScTemplateResult


class BaseResponseProcessor:
    def __init__(self):
        pass

    def __call__(self, response: Response, *args):
        raise NotImplementedError


class CreateElementsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScAddr]:
        return [ScAddr(addr_value) for addr_value in response.get(c.PAYLOAD)]


class CreateElementsBySCsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[bool]:
        return [bool(result) for result in response.get(c.PAYLOAD)]


class CheckElementsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScType]:
        return [ScType(type_value) for type_value in response.get(c.PAYLOAD)]


class DeleteElementsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> bool:
        return response.get(c.STATUS)


class SetLinkContentResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> bool:
        return response.get(c.STATUS)


class GetLinkContentResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScLinkContent]:
        response_payload = response.get(c.PAYLOAD)
        result = []
        for link in response_payload:
            str_type: str = link.get(c.TYPE)
            result.append(ScLinkContent(link.get(c.VALUE), ScLinkContentType[str_type.upper()]))
        return result


class GetLinksByContentResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[list[ScAddr]]:
        response_payload = response.get(c.PAYLOAD)
        if response_payload:
            return [[ScAddr(addr_value) for addr_value in addr_list] for addr_list in response_payload]
        return response_payload


class GetLinksByContentSubstringResponseProcessor(GetLinksByContentResponseProcessor):
    pass


class GetLinksContentsByContentSubstringResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[list[ScAddr]]:
        response_payload = response.get(c.PAYLOAD)
        return response_payload


class ResolveKeynodesResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScAddr]:
        response_payload = response.get(c.PAYLOAD)
        if response_payload:
            return [ScAddr(addr_value) for addr_value in response_payload]
        return response


class TemplateSearchResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScTemplateResult]:
        result = []
        if response.get(c.STATUS):
            response_payload = response.get(c.PAYLOAD)
            aliases = response_payload.get(c.ALIASES)
            all_addrs = response_payload.get(c.ADDRS)
            for addrs_list in all_addrs:
                addrs = [ScAddr(addr) for addr in addrs_list]
                result.append(ScTemplateResult(addrs, aliases))
        return result


class TemplateGenerateResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> ScTemplateResult:
        result = None
        if response.get(c.STATUS):
            response_payload = response.get(c.PAYLOAD)
            aliases = response_payload.get(c.ALIASES)
            addrs_list = response_payload.get(c.ADDRS)
            addrs = [ScAddr(addr) for addr in addrs_list]
            result = ScTemplateResult(addrs, aliases)
        return result


class EventsCreateResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *events: ScEvent) -> list[ScEvent]:
        result = []
        for count, event in enumerate(events):
            command_id = response.get(c.PAYLOAD)[count]
            sc_event = ScEvent(command_id, event.event_type, event.callback)
            session.set_event(sc_event)
            result.append(sc_event)
        return result


class EventsDestroyResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *events: ScEvent) -> bool:
        for event in events:
            session.drop_event(event.id)
        return response.get(c.STATUS)


class ResponseProcessor:
    _response_request_mapper = {
        c.ClientCommand.CREATE_ELEMENTS: CreateElementsResponseProcessor(),
        c.ClientCommand.CREATE_ELEMENTS_BY_SCS: CreateElementsBySCsResponseProcessor(),
        c.ClientCommand.CHECK_ELEMENTS: CheckElementsResponseProcessor(),
        c.ClientCommand.DELETE_ELEMENTS: DeleteElementsResponseProcessor(),
        c.ClientCommand.KEYNODES: ResolveKeynodesResponseProcessor(),
        c.ClientCommand.GET_LINK_CONTENT: GetLinkContentResponseProcessor(),
        c.ClientCommand.GET_LINKS_BY_CONTENT: GetLinksByContentResponseProcessor(),
        c.ClientCommand.GET_LINKS_BY_CONTENT_SUBSTRING: GetLinksByContentSubstringResponseProcessor(),
        c.ClientCommand.GET_LINKS_CONTENTS_BY_CONTENT_SUBSTRING: GetLinksContentsByContentSubstringResponseProcessor(),
        c.ClientCommand.SET_LINK_CONTENTS: SetLinkContentResponseProcessor(),
        c.ClientCommand.EVENTS_CREATE: EventsCreateResponseProcessor(),
        c.ClientCommand.EVENTS_DESTROY: EventsDestroyResponseProcessor(),
        c.ClientCommand.GENERATE_TEMPLATE: TemplateGenerateResponseProcessor(),
        c.ClientCommand.SEARCH_TEMPLATE: TemplateSearchResponseProcessor(),
    }

    def run(self, request_type: c.ClientCommand, *args, **kwargs):
        response_processor = self._response_request_mapper.get(request_type)
        return response_processor(*args, **kwargs)
