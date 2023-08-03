from __future__ import annotations

import abc

from sc_client.constants import common as c
from sc_client.core._sc_connection import ScConnection
from sc_client.models import Response, ScAddr, ScEvent, ScLinkContent, ScLinkContentType, ScTemplateResult, ScType


class BaseResponseProcessor(abc.ABC):
    def __init__(self, sc_connection: ScConnection) -> None:
        self._sc_connection = sc_connection

    @abc.abstractmethod
    def __call__(self, response: Response, *args: any) -> any:
        pass


class CreateElementsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScAddr]:
        return [ScAddr(addr_value) for addr_value in response.payload]


class CreateElementsBySCsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[bool]:
        return [bool(result) for result in response.payload]


class CheckElementsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScType]:
        return [ScType(type_value) for type_value in response.payload]


class DeleteElementsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> bool:
        return response.status


class SetLinkContentResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> bool:
        return response.status


class GetLinkContentResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScLinkContent]:
        response_payload = response.payload
        result = []
        for link in response_payload:
            str_type: str = link.get(c.TYPE)
            result.append(ScLinkContent(link.get(c.VALUE), ScLinkContentType[str_type.upper()]))
        return result


class GetLinksByContentResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[list[ScAddr]]:
        response_payload = response.payload
        if response_payload:
            return [[ScAddr(addr_value) for addr_value in addr_list] for addr_list in response_payload]
        return response_payload


class GetLinksByContentSubstringResponseProcessor(GetLinksByContentResponseProcessor):
    pass


class GetLinksContentsByContentSubstringResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[list[ScAddr]]:
        response_payload = response.payload
        return response_payload


class ResolveKeynodesResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScAddr]:
        response_payload = response.payload
        return [ScAddr(addr_value) for addr_value in response_payload]


class TemplateSearchResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScTemplateResult]:
        result = []
        if response.status:
            response_payload = response.payload
            aliases = response_payload.get(c.ALIASES)
            all_addrs = response_payload.get(c.ADDRS)
            for addrs_list in all_addrs:
                addrs = [ScAddr(addr) for addr in addrs_list]
                result.append(ScTemplateResult(addrs, aliases))
        return result


class TemplateGenerateResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> ScTemplateResult:
        result = None
        if response.status:
            response_payload = response.payload
            aliases = response_payload.get(c.ALIASES)
            addrs_list = response_payload.get(c.ADDRS)
            addrs = [ScAddr(addr) for addr in addrs_list]
            result = ScTemplateResult(addrs, aliases)
        return result


class EventsCreateResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *events: ScEvent) -> list[ScEvent]:
        result = []
        for count, event in enumerate(events):
            command_id = response.payload[count]
            sc_event = ScEvent(command_id, event.event_type, event.callback)
            self._sc_connection.set_event(sc_event)
            result.append(sc_event)
        return result


class EventsDestroyResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *events: ScEvent) -> bool:
        for event in events:
            self._sc_connection.drop_event(event.id)
        return response.status


class ResponseProcessor:
    def __init__(self, sc_connection: ScConnection) -> None:
        self._response_request_mapper: dict[int, BaseResponseProcessor] = {
            c.ClientCommand.CREATE_ELEMENTS: CreateElementsResponseProcessor(sc_connection),
            c.ClientCommand.CREATE_ELEMENTS_BY_SCS: CreateElementsBySCsResponseProcessor(sc_connection),
            c.ClientCommand.CHECK_ELEMENTS: CheckElementsResponseProcessor(sc_connection),
            c.ClientCommand.DELETE_ELEMENTS: DeleteElementsResponseProcessor(sc_connection),
            c.ClientCommand.KEYNODES: ResolveKeynodesResponseProcessor(sc_connection),
            c.ClientCommand.GET_LINK_CONTENT: GetLinkContentResponseProcessor(sc_connection),
            c.ClientCommand.GET_LINKS_BY_CONTENT: GetLinksByContentResponseProcessor(sc_connection),
            c.ClientCommand.GET_LINKS_BY_CONTENT_SUBSTRING: GetLinksByContentSubstringResponseProcessor(sc_connection),
            c.ClientCommand.GET_LINKS_CONTENTS_BY_CONTENT_SUBSTRING: (
                GetLinksContentsByContentSubstringResponseProcessor(sc_connection)
            ),
            c.ClientCommand.SET_LINK_CONTENTS: SetLinkContentResponseProcessor(sc_connection),
            c.ClientCommand.EVENTS_CREATE: EventsCreateResponseProcessor(sc_connection),
            c.ClientCommand.EVENTS_DESTROY: EventsDestroyResponseProcessor(sc_connection),
            c.ClientCommand.GENERATE_TEMPLATE: TemplateGenerateResponseProcessor(sc_connection),
            c.ClientCommand.SEARCH_TEMPLATE: TemplateSearchResponseProcessor(sc_connection),
        }

    def run(self, request_type: c.ClientCommand, *args, **kwargs) -> any:
        response_processor = self._response_request_mapper.get(request_type)
        return response_processor(*args, **kwargs)
