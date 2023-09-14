from __future__ import annotations

import asyncio
import json
import logging
from asyncio import Future
from typing import Awaitable, Callable

import websockets
import websockets.client
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK

from sc_client.constants import common, config
from sc_client.core.response import Response
from sc_client.models import AsyncScEvent, ScAddr
from sc_client.sc_exceptions import ErrorNotes, PayloadMaxSizeError, ScServerError


class AsyncScConnection:
    # pylint: disable=too-many-instance-attributes

    def __init__(self) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._url: str | None = None
        self._websocket = websockets.client.WebSocketClientProtocol()

        self._response_futures: dict[int, Future[Response]] = {}
        self._events_dict: dict[int, AsyncScEvent] = {}
        self._command_id: int = 0

        self.on_open: Callable[[], Awaitable[None]] = self._on_open_default
        self.on_close: Callable[[], Awaitable[None]] = self._on_close_default
        self.on_error: Callable[[Exception], Awaitable[None]] = self._on_error_default
        self.on_reconnect: Callable[[], Awaitable[None]] = self._on_reconnect_default

        self.reconnect_retries: int = config.SERVER_RECONNECT_RETRIES
        self.reconnect_delay: float = config.SERVER_RECONNECT_RETRY_DELAY

    async def connect(self, url: str = None) -> None:
        self._url = url or self._url
        try:
            self._websocket = await websockets.client.connect(self._url)
            self._logger.info("Connection open at url '%s'", self._url)
            await self.on_open()
            asyncio.create_task(self._handle_messages(), name="Handle messages")
            await asyncio.sleep(0)
        except ConnectionRefusedError:
            self._logger.error(ErrorNotes.CANNOT_CONNECT_TO_SC_SERVER)
            exception = ScServerError(ErrorNotes.CANNOT_CONNECT_TO_SC_SERVER)
            await self.on_error(exception)
            raise exception from None

    def is_connected(self) -> bool:
        return self._websocket.open

    async def _reconnect(self) -> None:
        try:
            await self.connect()
            await self.on_reconnect()
        except ScServerError:
            pass

    async def disconnect(self) -> None:
        if self.is_connected():
            await self._websocket.close()
            self._logger.info("Connection closed")
            await self.on_close()
        else:
            self._logger.info("Connection was already closed")

    async def _handle_messages(self) -> None:
        try:
            async for response_json in self._websocket:
                try:
                    await self._on_message(str(response_json))
                except (ScServerError, RuntimeError, ValueError) as e:
                    self._logger.error(e, exc_info=True)
        except ConnectionClosedOK:  # Connection closed by user
            for response_future in self._response_futures.values():
                response_future.cancel()
            self._response_futures.clear()
            return
        except ConnectionClosed:
            self._logger.error(ErrorNotes.CONNECTION_TO_SC_SERVER_LOST)
            exception = ScServerError(ErrorNotes.CONNECTION_TO_SC_SERVER_LOST)
            await self.on_error(exception)
            for response_future in self._response_futures.values():
                response_future.set_exception(exception)
            self._response_futures.clear()
            return

    async def _on_message(self, response_json: str) -> None:
        response = Response.load(response_json)
        if response.event:
            await self._on_event(response)
        else:
            self._response_futures[response.id].set_result(response)

    async def _on_event(self, response: Response):
        event = self.get_event(response.id)
        if event is None:
            self._logger.warning("Event id=%d is not found and cannot be executed", response.id)
            return
        self._logger.debug("Started %s", str(event))
        addrs: list[ScAddr] = [ScAddr(value) for value in response.payload]
        asyncio.create_task(event.callback(*addrs), name=f"ScEvent({event.id})")
        await asyncio.sleep(0)

    def set_event(self, sc_event: AsyncScEvent) -> None:
        self._events_dict[sc_event.id] = sc_event

    def get_event(self, event_id: int) -> AsyncScEvent | None:
        return self._events_dict.get(event_id)

    def drop_event(self, event_id: int) -> None:
        del self._events_dict[event_id]

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
            exception = PayloadMaxSizeError(f"Data is too large: {len_data} > {config.MAX_PAYLOAD_SIZE} bytes")
            await self.on_error(exception)
            raise exception
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
                exception = ScServerError(ErrorNotes.ALREADY_DISCONNECTED)
                await self.on_error(exception)
                raise exception from None
            except ConnectionClosed:
                if retries <= 0:
                    exception = ScServerError(ErrorNotes.SC_SERVER_TAKES_A_LONG_TIME_TO_RESPOND)
                    await self.on_error(exception)
                    raise exception from None
                retries -= 1
                self._logger.warning(
                    "Trying to reconnect in %d seconds (retries left: %s)", self.reconnect_delay, retries
                )
                await asyncio.sleep(self.reconnect_delay)
                await self._reconnect()

    async def _receive(self, command_id: int) -> Response:
        response_future = Future()
        self._response_futures[command_id] = response_future
        answer = await response_future
        return answer

    async def _on_open_default(self) -> None:
        pass

    async def _on_close_default(self) -> None:
        pass

    async def _on_error_default(self, exception: Exception) -> None:
        pass

    async def _on_reconnect_default(self) -> None:
        pass
