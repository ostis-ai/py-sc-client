from __future__ import annotations

from sc_client import session
from sc_client.constants import common as c
from sc_client.constants.sc_types import ScType
from sc_client.models import (
    Response,
    ScAddr,
    ScEventSubscription,
    ScEventSubscriptionParams,
    ScLinkContent,
    ScLinkContentType,
    ScTemplateResult,
)


class BaseResponseProcessor:
    def __init__(self):
        pass

    def __call__(self, response: Response, *args):
        raise NotImplementedError


class GenerateElementsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScAddr]:
        return [ScAddr(addr_value) for addr_value in response.get(c.PAYLOAD)]


class GenerateElementsBySCsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[bool]:
        return [bool(result) for result in response.get(c.PAYLOAD)]


class GetElementsTypesResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScType]:
        return [ScType(type_value) for type_value in response.get(c.PAYLOAD)]


class EraseElementsResponseProcessor(BaseResponseProcessor):
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


class SearchLinksByContentResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[list[ScAddr]]:
        response_payload = response.get(c.PAYLOAD)
        if response_payload:
            return [[ScAddr(addr_value) for addr_value in addr_list] for addr_list in response_payload]
        return response_payload


class SearchLinksByContentSubstringResponseProcessor(SearchLinksByContentResponseProcessor):
    pass


class SearchLinksContentsByContentSubstringResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[list[ScAddr]]:
        response_payload = response.get(c.PAYLOAD)
        return response_payload


class ResolveKeynodesResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> list[ScAddr]:
        response_payload = response.get(c.PAYLOAD)
        if response_payload:
            return [ScAddr(addr_value) for addr_value in response_payload]
        return response


class SearchByTemplateResponseProcessor(BaseResponseProcessor):
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


class GenerateByTemplateResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *_) -> ScTemplateResult:
        result = None
        if response.get(c.STATUS):
            response_payload = response.get(c.PAYLOAD)
            aliases = response_payload.get(c.ALIASES)
            addrs_list = response_payload.get(c.ADDRS)
            addrs = [ScAddr(addr) for addr in addrs_list]
            result = ScTemplateResult(addrs, aliases)
        return result


class CreateEventSubscriptionsResponseProcessor(BaseResponseProcessor):
    def __call__(
        self, response: Response, *event_subscriptions_params: ScEventSubscriptionParams
    ) -> list[ScEventSubscription]:
        result = []
        for count, event_subscription_param in enumerate(event_subscriptions_params):
            command_id = response.get(c.PAYLOAD)[count]
            event_subscription = ScEventSubscription(
                command_id, event_subscription_param.event_type, event_subscription_param.callback
            )
            session.set_event_subscription(event_subscription)
            result.append(event_subscription)
        return result


class DestroyEventSubscriptionsResponseProcessor(BaseResponseProcessor):
    def __call__(self, response: Response, *event_subscriptions: ScEventSubscription) -> bool:
        for event_subscription in event_subscriptions:
            session.drop_event_subscription(event_subscription.id)
        return response.get(c.STATUS)


class ResponseProcessor:
    _response_request_mapper = {
        c.ClientCommand.GENERATE_ELEMENTS: GenerateElementsResponseProcessor(),
        c.ClientCommand.GENERATE_ELEMENTS_BY_SCS: GenerateElementsBySCsResponseProcessor(),
        c.ClientCommand.GET_ELEMENTS_TYPES: GetElementsTypesResponseProcessor(),
        c.ClientCommand.ERASE_ELEMENTS: EraseElementsResponseProcessor(),
        c.ClientCommand.SEARCH_KEYNODES: ResolveKeynodesResponseProcessor(),
        c.ClientCommand.GET_LINK_CONTENT: GetLinkContentResponseProcessor(),
        c.ClientCommand.SEARCH_LINKS_BY_CONTENT: SearchLinksByContentResponseProcessor(),
        c.ClientCommand.SEARCH_LINKS_BY_CONTENT_SUBSTRING: SearchLinksByContentSubstringResponseProcessor(),
        c.ClientCommand.SEARCH_LINKS_CONTENTS_BY_CONTENT_SUBSTRING: SearchLinksContentsByContentSubstringResponseProcessor(),
        c.ClientCommand.SET_LINK_CONTENTS: SetLinkContentResponseProcessor(),
        c.ClientCommand.CREATE_EVENT_SUBSCRIPTIONS: CreateEventSubscriptionsResponseProcessor(),
        c.ClientCommand.DESTROY_EVENT_SUBSCRIPTIONS: DestroyEventSubscriptionsResponseProcessor(),
        c.ClientCommand.GENERATE_BY_TEMPLATE: GenerateByTemplateResponseProcessor(),
        c.ClientCommand.SEARCH_BY_TEMPLATE: SearchByTemplateResponseProcessor(),
    }

    def run(self, request_type: c.ClientCommand, *args, **kwargs):
        response_processor = self._response_request_mapper.get(request_type)
        return response_processor(*args, **kwargs)
