from __future__ import annotations

import asyncio
import logging
import time
from typing import Callable

import nest_asyncio

from sc_client import ScEventType
from sc_client.constants import sc_types
from sc_client.core.async_sc_client_ import AsyncScClient
from sc_client.models import (
    AsyncScEvent,
    AsyncScEventParams,
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


# noinspection PyProtectedMember
# pylint: disable=protected-access
class ScClient:
    def __init__(self) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        nest_asyncio.apply()
        self._async_sc_client = AsyncScClient()
        self._loop = asyncio.get_event_loop()

    def connect(self, url: str) -> None:
        self._loop.run_until_complete(self._async_sc_client.connect(url))

    def is_connected(self) -> bool:
        return self._async_sc_client.is_connected()

    def disconnect(self) -> None:
        self._loop.run_until_complete(self._async_sc_client.disconnect())

    def set_handlers(
        self,
        on_open: Callable[[], None] = None,
        on_close: Callable[[], None] = None,
        on_error: Callable[[Exception], None] = None,
        on_reconnect: Callable[[], None] = None,
    ) -> None:
        if on_open is None:
            async_on_open = self._async_sc_client._sc_connection.on_open
        else:

            async def async_on_open():
                on_open()

        if on_close is None:
            async_on_close = self._async_sc_client._sc_connection.on_close
        else:

            async def async_on_close():
                on_close()

        if on_error is None:
            async_on_error = self._async_sc_client._sc_connection.on_error
        else:

            async def async_on_error(e: Exception):
                on_error(e)

        if on_reconnect is None:
            async_on_reconnect = self._async_sc_client._sc_connection.on_reconnect
        else:

            async def async_on_reconnect():
                on_reconnect()

        self._async_sc_client.set_handlers(
            on_open=async_on_open, on_close=async_on_close, on_error=async_on_error, on_reconnect=async_on_reconnect
        )

    def set_reconnect_settings(self, retries: int = None, retry_delay: float = None) -> None:
        self._async_sc_client.set_reconnect_settings(retries, retry_delay)

    def check_elements(self, *addrs: ScAddr) -> list[ScType]:
        return self._loop.run_until_complete(self._async_sc_client.check_elements(*addrs))

    def create_elements(self, constr: ScConstruction) -> list[ScAddr]:
        return self._loop.run_until_complete(self._async_sc_client.create_elements(constr))

    def create_elements_by_scs(self, scs_text: SCsText) -> list[bool]:
        return self._loop.run_until_complete(self._async_sc_client.create_elements_by_scs(scs_text))

    def delete_elements(self, *addrs: ScAddr) -> bool:
        return self._loop.run_until_complete(self._async_sc_client.delete_elements(*addrs))

    def set_link_contents(self, *contents: ScLinkContent) -> bool:
        return self._loop.run_until_complete(self._async_sc_client.set_link_contents(*contents))

    def get_link_content(self, *addrs: ScAddr) -> list[ScLinkContent]:
        return self._loop.run_until_complete(self._async_sc_client.get_link_content(*addrs))

    def get_links_by_content(self, *contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
        return self._loop.run_until_complete(self._async_sc_client.get_links_by_content(*contents))

    def get_links_by_content_substring(self, *contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
        return self._loop.run_until_complete(self._async_sc_client.get_links_by_content_substring(*contents))

    def get_links_contents_by_content_substring(
        self, *contents: ScLinkContent | ScLinkContentData
    ) -> list[list[ScAddr]]:
        return self._loop.run_until_complete(self._async_sc_client.get_links_contents_by_content_substring(*contents))

    def resolve_keynodes(self, *params: ScIdtfResolveParams) -> list[ScAddr]:
        return self._loop.run_until_complete(self._async_sc_client.resolve_keynodes(*params))

    def template_search(
        self,
        template: ScTemplate | str | ScAddr,
        params: ScTemplateParams = None,
    ) -> list[ScTemplateResult]:
        return self._loop.run_until_complete(self._async_sc_client.template_search(template, params))

    def template_generate(
        self,
        template: ScTemplate | str | ScAddr,
        params: ScTemplateParams = None,
    ) -> ScTemplateResult:
        return self._loop.run_until_complete(self._async_sc_client.template_generate(template, params))

    # pylint: disable=cell-var-from-loop
    def events_create(self, *params: ScEventParams) -> list[ScEvent]:
        async_params: list[AsyncScEventParams] = []
        for param in params:

            async def async_callback(*addrs: ScAddr) -> None:
                param.callback(*addrs)

            async_event = AsyncScEventParams(param.addr, param.event_type, async_callback)
            async_params.append(async_event)
        async_events = self._loop.run_until_complete(self._async_sc_client.events_create(*async_params))
        events: list[ScEvent] = []
        for async_event in async_events:

            def callback(*addrs: ScAddr) -> None:
                self._loop.run_until_complete(async_event.callback(*addrs))

            event = ScEvent(async_event.id, async_event.event_type, callback)
            events.append(event)
        return events

    def events_destroy(self, *events: ScEvent) -> bool:
        async_events = [AsyncScEvent(event.id) for event in events]
        return self._loop.run_until_complete(self._async_sc_client.events_destroy(*async_events))

    def is_event_valid(self, event: ScEvent) -> bool:
        return self._async_sc_client.is_event_valid(AsyncScEvent(event.id))


def main():
    client = ScClient()
    client.connect("ws://localhost:8090/ws_json")
    constr = ScConstruction()
    constr.create_node(sc_types.NODE_CONST)
    start = time.time()
    res = [client.create_elements(constr) for _ in range(100)]
    timedelta = time.time() - start
    print(f"Created element: {res}\nin {timedelta} sec")
    client.disconnect()


def main_event():
    client = ScClient()
    client.connect("ws://localhost:8090/ws_json")

    constr = ScConstruction()
    constr.create_node(sc_types.NODE_CONST)
    constr.create_node(sc_types.NODE_CONST)
    results = client.create_elements(constr)
    src, trg = results

    def callback(*arrds: ScAddr):
        print(f"Call {arrds}")
        assert arrds[0] == src
        assert arrds[2] == trg

    param = ScEventParams(src, ScEventType.ADD_OUTGOING_EDGE, callback)
    event = client.events_create(param)[0]
    constr_call = ScConstruction()
    constr_call.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, src, trg)
    client.create_elements(constr_call)

    client.events_destroy(event)
    client.create_elements(constr_call)

    client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, force=True, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    main_event()
