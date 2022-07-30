"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from __future__ import annotations

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
    SCsText,
    ScTemplate,
    ScTemplateIdtf,
    ScTemplateParams,
    ScTemplateResult,
)


def connect(url: str) -> None:
    session.set_connection(url)


def is_connected() -> bool:
    return session.is_connection_established()


def disconnect() -> None:
    session.close_connection()


def check_elements(*addrs: ScAddr) -> list[ScType]:
    return session.execute(common.ClientCommand.CHECK_ELEMENTS, *addrs)


def create_elements(constr: ScConstruction) -> list[ScAddr]:
    return session.execute(common.ClientCommand.CREATE_ELEMENTS, constr)


def create_elements_by_scs(text: SCsText) -> list[bool]:
    return session.execute(common.ClientCommand.CREATE_ELEMENTS_BY_SCS, text)


def delete_elements(*addrs: ScAddr) -> bool:
    return session.execute(common.ClientCommand.DELETE_ELEMENTS, *addrs)


def set_link_contents(*contents: ScLinkContent) -> bool:
    return session.execute(common.ClientCommand.SET_LINK_CONTENTS, *contents)


def get_link_content(*addr: ScAddr) -> list[ScLinkContent]:
    return session.execute(common.ClientCommand.GET_LINK_CONTENT, *addr)


def get_links_by_content(*contents: ScLinkContent | str | int) -> list[list[ScAddr]]:
    return session.execute(common.ClientCommand.GET_LINKS_BY_CONTENT, *contents)


def get_links_by_content_substring(*contents: ScLinkContent | str | int) -> list[list[ScAddr]]:
    return session.execute(common.ClientCommand.GET_LINKS_BY_CONTENT_SUBSTRING, *contents)


def resolve_keynodes(*params: ScIdtfResolveParams) -> list[ScAddr]:
    return session.execute(common.ClientCommand.KEYNODES, *params)


def template_search(
    template: ScTemplate | str | ScTemplateIdtf | ScAddr, params: ScTemplateParams = None
) -> list[ScTemplateResult]:
    return session.execute(common.ClientCommand.SEARCH_TEMPLATE, template, params)


def template_generate(
    template: ScTemplate | str | ScTemplateIdtf | ScAddr, params: ScTemplateParams = None
) -> ScTemplateResult:
    return session.execute(common.ClientCommand.GENERATE_TEMPLATE, template, params)


def events_create(*events: ScEventParams) -> list[ScEvent]:
    return session.execute(common.ClientCommand.EVENTS_CREATE, *events)


def events_destroy(*events: ScEvent) -> bool:
    return session.execute(common.ClientCommand.EVENTS_DESTROY, *events)


def is_event_valid(event: ScEvent) -> bool:
    return bool(session.get_event(event.id))
