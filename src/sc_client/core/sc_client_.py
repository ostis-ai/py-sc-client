from __future__ import annotations

import asyncio
import logging
from typing import Callable

import nest_asyncio

from sc_client.core.asc_client_ import AScClient
from sc_client.models import (
    AScEvent,
    AScEventParams,
    ScAddr,
    ScConstruction,
    ScEvent,
    ScEventParams,
    ScIdtfResolveParams,
    ScLinkContent,
    ScLinkContentData,
    SCsText,
    ScTemplate,
    ScTemplateParams,
    ScTemplateResult,
    ScType,
)
from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError


# noinspection PyProtectedMember
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
class ScClient:
    def __init__(self) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        nest_asyncio.apply()
        self._asc_client = AScClient()
        self._loop = asyncio.get_event_loop()

    def connect(self, url: str) -> None:
        self._loop.run_until_complete(self._asc_client.connect(url))

    def is_connected(self) -> bool:
        return self._asc_client.is_connected()

    def disconnect(self) -> None:
        self._loop.run_until_complete(self._asc_client.disconnect())

    def set_on_open_handler(self, on_open: Callable[[], None]) -> None:
        async def async_on_open():
            on_open()

        self._asc_client.set_on_open_handler(async_on_open)

    def set_on_close_handler(self, on_close: Callable[[], None]) -> None:
        async def async_on_close():
            on_close()

        self._asc_client.set_on_close_handler(async_on_close)

    def set_on_error_handler(self, on_error: Callable[[Exception], None]) -> None:
        async def async_on_error(e: Exception):
            on_error(e)

        self._asc_client.set_on_error_handler(async_on_error)

    def set_on_reconnect_handler(self, on_reconnect: Callable[[], None]) -> None:
        async def async_on_reconnect():
            on_reconnect()

        self._asc_client.set_on_reconnect_handler(async_on_reconnect)

    def set_reconnect_settings(self, retries: int = None, retry_delay: float = None) -> None:
        self._asc_client.set_reconnect_settings(retries, retry_delay)

    def check_elements(self, *addrs: ScAddr) -> list[ScType]:
        return self._loop.run_until_complete(self._asc_client.check_elements(*addrs))

    def create_elements(self, constr: ScConstruction) -> list[ScAddr]:
        return self._loop.run_until_complete(self._asc_client.create_elements(constr))

    def create_elements_by_scs(self, scs_text: SCsText) -> list[bool]:
        return self._loop.run_until_complete(self._asc_client.create_elements_by_scs(scs_text))

    def delete_elements(self, *addrs: ScAddr) -> bool:
        return self._loop.run_until_complete(self._asc_client.delete_elements(*addrs))

    def set_link_contents(self, *contents: ScLinkContent) -> bool:
        return self._loop.run_until_complete(self._asc_client.set_link_contents(*contents))

    def get_link_content(self, *addrs: ScAddr) -> list[ScLinkContent]:
        return self._loop.run_until_complete(self._asc_client.get_link_content(*addrs))

    def get_links_by_content(self, *contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
        return self._loop.run_until_complete(self._asc_client.get_links_by_content(*contents))

    def get_links_by_content_substring(self, *contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
        return self._loop.run_until_complete(self._asc_client.get_links_by_content_substring(*contents))

    def get_links_contents_by_content_substring(
        self, *contents: ScLinkContent | ScLinkContentData
    ) -> list[list[ScAddr]]:
        return self._loop.run_until_complete(self._asc_client.get_links_contents_by_content_substring(*contents))

    def resolve_keynodes(self, *params: ScIdtfResolveParams) -> list[ScAddr]:
        return self._loop.run_until_complete(self._asc_client.resolve_keynodes(*params))

    def template_search(
        self,
        template: ScTemplate | str | ScAddr,
        params: ScTemplateParams = None,
    ) -> list[ScTemplateResult]:
        return self._loop.run_until_complete(self._asc_client.template_search(template, params))

    def template_generate(
        self,
        template: ScTemplate | str | ScAddr,
        params: ScTemplateParams = None,
    ) -> ScTemplateResult:
        return self._loop.run_until_complete(self._asc_client.template_generate(template, params))

    # pylint: disable=cell-var-from-loop
    def events_create(self, *params: ScEventParams) -> list[ScEvent]:
        if not all(isinstance(param, ScEventParams) for param in params):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScEventParams")
        async_params: list[AScEventParams] = []
        for param in params:

            async def async_callback(*addrs: ScAddr) -> None:
                param.callback(*addrs)

            async_event = AScEventParams(param.addr, param.event_type, async_callback)
            async_params.append(async_event)
        async_events = self._loop.run_until_complete(self._asc_client.events_create(*async_params))
        events: list[ScEvent] = []
        for async_event in async_events:

            def callback(*addrs: ScAddr) -> None:
                self._loop.run_until_complete(async_event.callback(*addrs))

            event = ScEvent(async_event.id, async_event.event_type, callback)
            events.append(event)
        return events

    def events_destroy(self, *events: ScEvent) -> bool:
        if not all(isinstance(event, ScEvent) for event in events):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScEvent")
        async_events = [AScEvent(event.id) for event in events]
        return self._loop.run_until_complete(self._asc_client.events_destroy(*async_events))

    def is_event_valid(self, event: ScEvent) -> bool:
        if not isinstance(event, ScEvent):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScEvent")
        return self._asc_client.is_event_valid(AScEvent(event.id))
