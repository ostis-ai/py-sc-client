from __future__ import annotations

import asyncio
import json
import logging
from typing import Awaitable, Callable

import websockets
import websockets.client
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK

from sc_client import ScAddr, ScEvent
from sc_client.constants import common, config
from sc_client.models import Response
from sc_client.sc_exceptions import ErrorNotes, PayloadMaxSizeError, ScServerError
from sc_client.sc_exceptions.sc_exeptions_ import ScConnectionError


class AsyncScConnection:
    def __init__(self) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._url: str | None = None
        self._websocket = websockets.client.WebSocketClientProtocol()

        self._responses_dict: dict[int, Response] = {}
        self._events_dict: dict[int, ScEvent] = {}
        self._command_id: int = 0
        self.reconnect_retries: int = config.SERVER_RECONNECT_RETRIES
        self.reconnect_delay: float = config.SERVER_RECONNECT_RETRY_DELAY

        self.on_open: Callable[[], Awaitable[None]] = self._on_open_default
        self.on_close: Callable[[], Awaitable[None]] = self._on_close_default
        self.on_error: Callable[[Exception], Awaitable[None]] = self._on_error_default
        self.on_reconnect: Callable[[], Awaitable[None]] = self._on_reconnect_default

    async def connect(self, url: str = None) -> None:
        self._url = url or self._url
        try:
            self._websocket = await websockets.client.connect(self._url)
            self._logger.info("connected")
            await self.on_open()
            await self._start_handle_messages()
        except ConnectionRefusedError as e:
            self._logger.error("Cannot to connect to sc-server")
            raise ScServerError(ErrorNotes.CANNOT_CONNECT_TO_SC_SERVER) from e

    async def _start_handle_messages(self):
        asyncio.create_task(self.handle_messages())
        await asyncio.sleep(0)

    async def handle_messages(self) -> None:
        try:
            async for message in self._websocket:
                await self._on_message(str(message))
        except ConnectionClosedOK:
            # Everything is OK
            return
        except ConnectionClosed as e:
            self._logger.error(e, exc_info=True)
            await self.on_error(e)
            raise ScServerError(ErrorNotes.CONNECTION_TO_SC_SERVER_LOST) from e

    async def disconnect(self) -> None:
        if self.is_connected():
            await self._websocket.close()
            self._logger.info("Connection closed")
            await self.on_close()
        else:
            self._logger.info("Connection was already closed")

    def is_connected(self):
        return self._websocket.open

    async def send_message(self, request_type: common.RequestType, payload: any) -> Response:
        self._command_id += 1
        command_id = self._command_id
        data = json.dumps(
            {
                common.ID: command_id,
                common.TYPE: request_type.value,
                common.PAYLOAD: payload,
            }
        )
        len_data = len(bytes(data, "utf-8"))
        if len_data > config.MAX_PAYLOAD_SIZE:
            raise PayloadMaxSizeError(f"Data is too large: {len_data} > {config.MAX_PAYLOAD_SIZE} bytes")
        await self._send_with_reconnect(data)
        response = await self._receive(command_id)
        return response

    async def _send_with_reconnect(self, data: str) -> None:
        retries: int = self.reconnect_retries
        while True:
            try:
                await self._websocket.send(data)
                return
            except ConnectionClosedOK:
                # Everything is OK
                return
            except ConnectionClosed as e:
                if not retries:
                    raise ScConnectionError(ErrorNotes.SC_SERVER_TAKES_A_LONG_TIME_TO_RESPOND) from e
                retries -= 1
                self._logger.warning(f"Trying to reconnect in {self.reconnect_delay} seconds (retries left: {retries})")
                await asyncio.sleep(self.reconnect_delay)
                await self.connect()
                if self.is_connected():
                    await self.on_reconnect()

    async def _receive(self, command_id: int) -> Response:
        while (answer := self._responses_dict.get(command_id)) is None and self._websocket.open:
            await asyncio.sleep(config.SERVER_ANSWER_CHECK_TIME)
        if answer is None:
            raise ScConnectionError(ErrorNotes.CONNECTION_TO_SC_SERVER_LOST)
        del self._responses_dict[command_id]
        return answer

    async def _on_message(self, response: str) -> None:
        response = Response.load(response)
        if response.event:
            if event := self.get_event(response.id):
                self._logger.debug(f"Started {str(event)}")
                await event.callback(*(ScAddr(addr) for addr in response.payload))
        else:
            self._responses_dict[response.id] = response

    def set_event(self, sc_event: ScEvent) -> None:
        self._events_dict[sc_event.id] = sc_event

    def get_event(self, event_id: int) -> ScEvent | None:
        return self._events_dict.get(event_id)

    def drop_event(self, event_id: int) -> None:
        del self._events_dict[event_id]

    async def _on_open_default(self):
        pass
        # self._logger.info("_on_open_default")

    async def _on_close_default(self):
        pass
        # self._logger.info("_on_close_default")

    async def _on_error_default(self, e: Exception) -> None:
        # pass
        self._logger.error(e)

    async def _on_reconnect_default(self) -> None:
        pass
        # self._logger.info("_on_reconnect_default")
