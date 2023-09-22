from __future__ import annotations

import asyncio
import logging
from typing import Any

from websockets.exceptions import ConnectionClosed, ConnectionClosedOK

from sc_client.core import AScClient, ScClient
from sc_client.core.asc_connection import AScConnection
from sc_client.testing.response_callback import ResponseCallback


class WebsocketStub:
    """Stub for async websockets.client.WebSocketClientProtocol"""

    is_connection_lost: bool = False
    # pylint: disable=unsubscriptable-object
    messages: asyncio.Queue[str] = asyncio.Queue()
    message_callbacks: asyncio.LifoQueue[ResponseCallback] = asyncio.LifoQueue()

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.is_connected = False

    async def connect(self, url: str):
        await asyncio.sleep(0.01)
        if not url:
            raise ConnectionRefusedError
        if self.__class__.is_connection_lost:
            raise ConnectionRefusedError
        self.logger.info("Connection established")
        self.is_connected = True

    async def close(self):
        await asyncio.sleep(0.01)
        self.logger.info("Connection closed")
        self.is_connected = False
        # await self.messages.join()

    @property
    def open(self) -> bool:
        return self.is_connected and not self.is_connection_lost

    async def send(self, message: str) -> None:
        self._assert_connection()
        asyncio.create_task(self._add_response(message))
        await asyncio.sleep(0)

    async def _add_response(self, message: str) -> None:
        callback = await self.message_callbacks.get()
        await asyncio.sleep(callback.delay)
        try:
            self._assert_connection()
        except ConnectionClosed:
            return
        response = await callback.process_response(message)
        await self.messages.put(response)

    async def receive(self) -> str:
        while True:
            self._assert_connection()
            try:
                return self.messages.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0)

    def _assert_connection(self) -> None:
        if self.__class__.is_connection_lost:
            raise ConnectionClosed(None, None)
        if not self.is_connected:
            raise ConnectionClosedOK(None, None)

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.receive()

    # noinspection PyProtectedMember
    # pylint: disable=protected-access
    @classmethod
    def of(cls, obj: AScConnection | AScClient | ScClient) -> WebsocketStub:
        return (
            obj
            if isinstance(obj, AScConnection)
            else (obj if isinstance(obj, AScClient) else obj._asc_client)._sc_connection
        )._websocket

    async def set_message_callback(self, callback: ResponseCallback) -> None:
        await self.message_callbacks.put(callback)

    def sync_set_message_callback(self, callback: ResponseCallback) -> None:
        asyncio.get_event_loop().run_until_complete(self.message_callbacks.put(callback))

    @staticmethod
    def lose_connection() -> ConnectionEstablisher:
        """The context manager to lose and establish connection"""
        return ConnectionEstablisher()


class ConnectionEstablisher:
    async def __aenter__(self):
        WebsocketStub.is_connection_lost = True
        await asyncio.sleep(0)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        WebsocketStub.is_connection_lost = False
        await asyncio.sleep(0)


async def websockets_client_connect_patch(url: str) -> WebsocketStub:
    websocket_mock = WebsocketStub()
    await websocket_mock.connect(url)
    return websocket_mock
