"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from __future__ import annotations

import warnings

from sc_client import session
from sc_client.constants import common, exceptions
from sc_client.constants.numeric import SERVER_RECONNECT_RETRIES, SERVER_RECONNECT_RETRY_DELAY
from sc_client.constants.sc_types import ScType
from sc_client.models import (
    ScAddr,
    ScConstruction,
    ScEventSubscription,
    ScEventSubscriptionParams,
    ScIdtfResolveParams,
    ScLinkContent,
    SCsText,
    ScTemplate,
    ScTemplateIdtf,
    ScTemplateParams,
    ScTemplateResult,
)
from sc_client.models.sc_construction import ScLinkContentData


def connect(url: str) -> None:
    session.set_connection(url)


def is_connected() -> bool:
    return session.is_connected()


def disconnect() -> None:
    session.close_connection()


def set_error_handler(callback) -> None:
    session.set_error_handler(callback)


def set_reconnect_handler(**reconnect_kwargs) -> None:
    session.set_reconnect_handler(
        reconnect_kwargs.get("reconnect_handler", session.default_reconnect_handler),
        reconnect_kwargs.get("post_reconnect_handler"),
        reconnect_kwargs.get("reconnect_retries", SERVER_RECONNECT_RETRIES),
        reconnect_kwargs.get("reconnect_retry_delay", SERVER_RECONNECT_RETRY_DELAY),
    )


def get_elements_types(*addrs: ScAddr) -> list[ScType]:
    return session.execute(common.ClientCommand.GET_ELEMENTS_TYPES, *addrs)


def check_elements(*addrs: ScAddr) -> list[ScType]:
    warnings.warn(
        "ScClient 'check_elements' method is deprecated. Use `get_elements_types` method instead.", DeprecationWarning
    )
    return get_elements_types(*addrs)


def generate_elements(constr: ScConstruction) -> list[ScAddr]:
    return session.execute(common.ClientCommand.GENERATE_ELEMENTS, constr)


def create_elements(constr: ScConstruction) -> list[ScAddr]:
    warnings.warn(
        "ScClient 'create_elements' method is deprecated. Use `generate_elements` method instead.", DeprecationWarning
    )
    return generate_elements(constr)


def generate_elements_by_scs(text: SCsText) -> list[bool]:
    return session.execute(common.ClientCommand.GENERATE_ELEMENTS_BY_SCS, text)


def create_elements_by_scs(text: SCsText) -> list[bool]:
    warnings.warn(
        "ScClient 'create_elements_by_scs' method is deprecated. Use `generate_elements_by_scs` method instead.",
        DeprecationWarning,
    )
    return generate_elements_by_scs(text)


def erase_elements(*addrs: ScAddr) -> bool:
    return session.execute(common.ClientCommand.ERASE_ELEMENTS, *addrs)


def delete_elements(*addrs: ScAddr) -> bool:
    warnings.warn(
        "ScClient 'delete_elements' method is deprecated. Use `erase_elements` method instead.", DeprecationWarning
    )
    return erase_elements(*addrs)


def set_link_contents(*contents: ScLinkContent) -> bool:
    return session.execute(common.ClientCommand.SET_LINK_CONTENTS, *contents)


def get_link_content(*addr: ScAddr) -> list[ScLinkContent]:
    return session.execute(common.ClientCommand.GET_LINK_CONTENT, *addr)


def search_links_by_contents(*contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
    return session.execute(common.ClientCommand.SEARCH_LINKS_BY_CONTENT, *contents)


def get_links_by_content(*contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
    warnings.warn(
        "ScClient 'get_links_by_content' method is deprecated. Use `search_links_by_contents` method instead.",
        DeprecationWarning,
    )
    return search_links_by_contents(*contents)


def search_links_by_contents_substrings(*contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
    return session.execute(common.ClientCommand.SEARCH_LINKS_BY_CONTENT_SUBSTRING, *contents)


def get_links_by_content_substring(*contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
    warnings.warn(
        "ScClient 'get_links_by_content_substring' method is deprecated. Use `search_links_by_contents_substrings` method instead.",
        DeprecationWarning,
    )
    return search_links_by_contents_substrings(*contents)


def search_link_contents_by_content_substrings(*contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
    return session.execute(common.ClientCommand.SEARCH_LINKS_CONTENTS_BY_CONTENT_SUBSTRING, *contents)


def get_links_contents_by_content_substring(*contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
    warnings.warn(
        "ScClient 'get_links_contents_by_content_substring' method is deprecated. Use `search_link_contents_by_content_substrings` method instead.",
        DeprecationWarning,
    )
    return search_link_contents_by_content_substrings(*contents)


def resolve_keynodes(*params: ScIdtfResolveParams) -> list[ScAddr]:
    return session.execute(common.ClientCommand.SEARCH_KEYNODES, *params)


def search_by_template(
    template: ScTemplate | str | ScTemplateIdtf | ScAddr, params: ScTemplateParams = None
) -> list[ScTemplateResult]:
    return session.execute(common.ClientCommand.SEARCH_BY_TEMPLATE, template, params)


def template_search(
    template: ScTemplate | str | ScTemplateIdtf | ScAddr, params: ScTemplateParams = None
) -> list[ScTemplateResult]:
    warnings.warn(
        "ScClient 'template_search' method is deprecated. Use `search_by_template` method instead.", DeprecationWarning
    )
    return search_by_template(template, params)


def generate_by_template(
    template: ScTemplate | str | ScTemplateIdtf | ScAddr, params: ScTemplateParams = None
) -> ScTemplateResult:
    return session.execute(common.ClientCommand.GENERATE_BY_TEMPLATE, template, params)


def template_generate(
    template: ScTemplate | str | ScTemplateIdtf | ScAddr, params: ScTemplateParams = None
) -> ScTemplateResult:
    warnings.warn(
        "ScClient 'template_generate' method is deprecated. Use `generate_by_template` method instead.",
        DeprecationWarning,
    )
    return generate_by_template(template, params)


def create_elementary_event_subscriptions(*params: ScEventSubscriptionParams) -> list[ScEventSubscription]:
    return session.execute(common.ClientCommand.CREATE_EVENT_SUBSCRIPTIONS, *params)


def events_create(*params: ScEventSubscriptionParams) -> list[ScEventSubscription]:
    warnings.warn(
        "ScClient 'evens_create' method is deprecated. Use `create_elementary_event_subscriptions` method instead.",
        DeprecationWarning,
    )
    return create_elementary_event_subscriptions(*params)


def destroy_elementary_event_subscriptions(*event_subscriptions: ScEventSubscription) -> bool:
    return session.execute(common.ClientCommand.DESTROY_EVENT_SUBSCRIPTIONS, *event_subscriptions)


def events_destroy(*event_subscriptions: ScEventSubscription) -> bool:
    warnings.warn(
        "ScClient 'events_destroy' method is deprecated. Use `destroy_elementary_event_subscriptions` method instead.",
        DeprecationWarning,
    )
    return destroy_elementary_event_subscriptions(*event_subscriptions)


def is_event_subscription_valid(event_subscription: ScEventSubscription) -> bool:
    if not isinstance(event_subscription, ScEventSubscription):
        raise exceptions.InvalidTypeError("expected object types: ScEventSubscription")
    return bool(session.get_event_subscription(event_subscription.id))


def is_event_valid(event_subscription: ScEventSubscription) -> bool:
    warnings.warn(
        "ScClient 'is_event_valid' method is deprecated. Use `is_event_subscription_valid` method instead.",
        DeprecationWarning,
    )
    return is_event_subscription_valid(event_subscription)
