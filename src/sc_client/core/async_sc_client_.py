from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import Awaitable, Callable, get_origin

from sc_client.constants import common, sc_types
from sc_client.constants.common import CommandTypes, RequestType
from sc_client.core.async_sc_connection import AsyncScConnection
from sc_client.models import (
    Response,
    ScAddr,
    ScConstruction,
    ScEvent,
    ScEventParams,
    ScIdtfResolveParams,
    ScLinkContent,
    ScLinkContentData,
    ScLinkContentType,
    SCs,
    SCsText,
    ScTemplate,
    ScTemplateParams,
    ScTemplateResult,
    ScTemplateValue,
    ScType,
)
from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError, ScServerError


class AsyncScClient:
    def __init__(self) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._sc_connection = AsyncScConnection()

    async def connect(self, url: str) -> None:
        await self._sc_connection.connect(url)

    def is_connected(self) -> bool:
        return self._sc_connection.is_connected()

    async def disconnect(self) -> None:
        await self._sc_connection.disconnect()

    def set_error_handler(self, callback) -> None:
        self._sc_connection.on_error = callback

    def set_reconnect_handler(
        self,
        reconnect_callback: Callable[[], Awaitable[None]] = None,
        connect_callback: Callable[[], Awaitable[None]] = None,
        reconnect_retries: int = None,
        reconnect_retry_delay: float = None,
    ) -> None:
        self._sc_connection.on_reconnect = reconnect_callback or self._sc_connection.on_reconnect
        self._sc_connection.on_open = connect_callback or self._sc_connection.on_open
        self._sc_connection.reconnect_retries = reconnect_retries or self._sc_connection.reconnect_retries
        self._sc_connection.reconnect_retry_delay = reconnect_retry_delay or self._sc_connection.reconnect_retry_delay

    async def check_elements(self, *addrs: ScAddr) -> list[ScType]:
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        payload = [addr.value for addr in addrs]
        response = await self._send_message(RequestType.CHECK_ELEMENTS, payload)
        data = [ScType(type_value) for type_value in response.payload]
        return data

    async def create_elements(self, constr: ScConstruction) -> list[ScAddr]:
        if not isinstance(constr, ScConstruction):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScConstruction")
        payload = []
        for command in constr.commands:
            if command.el_type.is_node():
                payload_part = {
                    common.ELEMENT: common.Elements.NODE,
                    common.TYPE: command.el_type.value,
                }
                payload.append(payload_part)
            elif command.el_type.is_edge():
                payload_part = {
                    common.ELEMENT: common.Elements.EDGE,
                    common.TYPE: command.el_type.value,
                    common.SOURCE: self._transform_edge_info(constr, command.data.get(common.SOURCE)),
                    common.TARGET: self._transform_edge_info(constr, command.data.get(common.TARGET)),
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
        response = await self._send_message(RequestType.CREATE_ELEMENTS, payload)
        return [ScAddr(addr_value) for addr_value in response.payload]

    @staticmethod
    def _transform_edge_info(construction: ScConstruction, element: ScAddr | str) -> any:
        return (
            {common.TYPE: common.Types.ADDR, common.VALUE: element.value}
            if isinstance(element, ScAddr)
            else {
                common.TYPE: common.Types.REF,
                common.VALUE: construction.get_index(element),
            }
        )

    async def create_elements_by_scs(self, scs_text: SCsText) -> list[bool]:
        if not isinstance(scs_text, list) or any(isinstance(n, (str, SCs)) for n in scs_text):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "string or SCs")
        payload = [
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
        response = await self._send_message(RequestType.CREATE_ELEMENTS_BY_SCS, payload)
        return [bool(result) for result in response.payload]

    async def delete_elements(self, *addrs: ScAddr) -> bool:
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        payload = [addr.value for addr in addrs]
        response = await self._send_message(RequestType.DELETE_ELEMENTS, payload)
        return response.status

    async def set_link_contents(self, *contents: ScLinkContent) -> bool:
        if not all(isinstance(content, ScLinkContent) for content in contents):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        payload = [
            {
                common.COMMAND: CommandTypes.SET,
                common.TYPE: content.type_to_str(),
                common.DATA: content.data,
                common.ADDR: content.addr.value,
            }
            for content in contents
        ]
        response = await self._send_message(RequestType.CONTENT, payload)
        return response.status

    async def get_link_content(self, *addrs: ScAddr) -> list[ScLinkContent]:
        if not all(isinstance(addr, ScAddr) for addr in addrs):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR)
        payload = [
            {
                common.COMMAND: CommandTypes.GET,
                common.ADDR: addr.value,
            }
            for addr in addrs
        ]
        response = await self._send_message(RequestType.CONTENT, payload)
        result = []
        for link in response.payload:
            str_type: str = link.get(common.TYPE)
            result.append(ScLinkContent(link.get(common.VALUE), ScLinkContentType[str_type.upper()]))
        return result

    async def get_links_by_content(self, *contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
        return await self._process_get_links(*contents, command=CommandTypes.FIND)

    async def get_links_by_content_substring(self, *contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
        return await self._process_get_links(*contents, command=CommandTypes.FIND_LINKS_BY_SUBSTRING)

    async def get_links_contents_by_content_substring(
        self, *contents: ScLinkContent | ScLinkContentData
    ) -> list[list[ScAddr]]:
        return await self._process_get_links(*contents, command=CommandTypes.FIND_LINKS_CONTENTS_BY_CONTENT_SUBSTRING)

    async def _process_get_links(
        self, *contents: ScLinkContent | ScLinkContentData, command: str
    ) -> list[list[ScAddr]]:
        if not all(isinstance(content, (ScLinkContent, str, int, float)) for content in contents):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScLinkContent, str, int or float")
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
        payload = [
            {
                common.COMMAND: command,
                common.DATA: content.data,
            }
            for content in link_contents
        ]
        response = await self._sc_connection.send_message(RequestType.CONTENT, payload)
        if not response.payload:
            return response.payload
        return [[ScAddr(addr_value) for addr_value in addr_list] for addr_list in response.payload]

    async def resolve_keynodes(self, *params: ScIdtfResolveParams) -> list[ScAddr]:
        if not all(isinstance(par, ScIdtfResolveParams) for par in params):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScIdtfResolveParams")
        payload = []
        for idtf_param in params:
            keynode_type = idtf_param.type
            if keynode_type and keynode_type.is_valid():
                payload_item = {
                    common.COMMAND: CommandTypes.RESOLVE,
                    common.IDTF: idtf_param.idtf,
                    common.ELEMENT_TYPE: idtf_param.type.value,
                }
            else:
                payload_item = {
                    common.COMMAND: CommandTypes.FIND,
                    common.IDTF: idtf_param.idtf,
                }
            payload.append(payload_item)
        response = await self._send_message(RequestType.KEYNODES, payload)
        return [ScAddr(addr_value) for addr_value in response.payload]

    async def template_search(
        self,
        template: ScTemplate | str | ScAddr,
        params: ScTemplateParams = None,
    ) -> list[ScTemplateResult]:
        payload = self._create_template_payload(template, params)
        response = await self._send_message(RequestType.SEARCH_TEMPLATE, payload)
        result = []
        if response.status:
            response_payload = response.payload
            aliases = response_payload.get(common.ALIASES)
            all_addrs = response_payload.get(common.ADDRS)
            for addrs_list in all_addrs:
                addrs = [ScAddr(addr) for addr in addrs_list]
                result.append(ScTemplateResult(addrs, aliases))
        return result

    async def template_generate(
        self,
        template: ScTemplate | str | ScAddr,
        params: ScTemplateParams = None,
    ) -> ScTemplateResult:
        payload = self._create_template_payload(template, params)
        response = await self._send_message(RequestType.GENERATE_TEMPLATE, payload)
        result = None
        if response.status:
            response_payload = response.payload
            aliases = response_payload.get(common.ALIASES)
            addrs_list = response_payload.get(common.ADDRS)
            addrs = [ScAddr(addr) for addr in addrs_list]
            result = ScTemplateResult(addrs, aliases)
        return result

    @classmethod
    def _create_template_payload(cls, template: ScTemplate | str | ScAddr, params: ScTemplateParams = None) -> any:
        if not isinstance(template, (ScTemplate, str, ScAddr)):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScTemplate, str or ScArrd")
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
            payload_template = cls._process_template(template)

        payload_params = {}
        if params is not None:
            if not isinstance(params, get_origin(ScTemplateParams)):
                raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScTemplateParams")
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

    async def events_create(self, *events: ScEventParams) -> list[ScEvent]:
        if not all(isinstance(event, ScEventParams) for event in events):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScEventParams")
        payload_create = [{common.TYPE: event.event_type.value, common.ADDR: event.addr.value} for event in events]
        payload = {CommandTypes.CREATE: payload_create}
        response = await self._send_message(RequestType.EVENTS, payload)
        result: list[ScEvent] = []
        for count, event in enumerate(events):
            command_id = response.payload[count]
            sc_event = ScEvent(command_id, event.event_type, event.callback)
            self._sc_connection.set_event(sc_event)
            result.append(sc_event)
        return result

    async def events_destroy(self, *events: ScEvent) -> bool:
        if not all(isinstance(event, ScEvent) for event in events):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScEvent")
        payload = {CommandTypes.DELETE: [event.id for event in events]}
        response = await self._send_message(RequestType.EVENTS, payload)
        for event in events:
            self._sc_connection.drop_event(event.id)
        return response.status

    def is_event_valid(self, event: ScEvent) -> bool:
        if not isinstance(event, ScEvent):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScEvent")
        return bool(self._sc_connection.get_event(event.id))

    async def _send_message(self, request_type: common.RequestType, payload: any) -> Response:
        response = await self._sc_connection.send_message(request_type, payload)
        if not response.errors:
            return response
        error_msgs: list[str] = []
        if isinstance(response.errors, str):
            error_msgs.append(response.errors)
        else:
            for error in response.errors:
                payload_part = f"\nPayload: {payload[int(error.get(common.REF))]}" if error.get(common.REF) else ""
                error_msgs.append(error.get(common.MESSAGE) + payload_part)
        error_msg = "\n".join(error_msgs)
        error = ScServerError(error_msg)
        self._logger.error(error, exc_info=True)
        raise error


async def main():
    client = AsyncScClient()
    await client.connect("ws://localhost:8090/ws_json")
    constr = ScConstruction()
    constr.create_node(sc_types.NODE_CONST)
    start = time.time()
    res = await asyncio.gather(*[client.create_elements(constr) for _ in range(100)])
    timedelta = time.time() - start
    print(f"Created element: {res}\nin {timedelta} sec")
    await client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, force=True, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    asyncio.run(main())
