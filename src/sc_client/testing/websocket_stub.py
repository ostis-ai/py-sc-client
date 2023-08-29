from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

from websockets.exceptions import ConnectionClosed, ConnectionClosedOK

from sc_client.core.async_sc_connection import AsyncScConnection


class WebsocketStub:
    """Stub for async websockets.client.WebSocketClientProtocol"""

    is_connection_lost: bool = False

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.is_connected = False
        # pylint: disable=unsubscriptable-object
        self.messages: asyncio.Queue[str] = asyncio.Queue()
        self.message_callbacks: asyncio.LifoQueue[Callable[[str], str]] = asyncio.LifoQueue()

    async def connect(self, url: str):
        await asyncio.sleep(0.01)
        if not url:
            raise ConnectionRefusedError
        if self.__class__.is_connection_lost:
            raise ConnectionRefusedError
        self.logger.info("Mock connection")
        self.is_connected = True

    async def close(self):
        await asyncio.sleep(0.01)
        self.logger.info("Mock disonnection")
        self.is_connected = False
        # await self.messages.join()

    @property
    def open(self) -> bool:
        return self.is_connected

    async def send(self, message: str) -> None:
        self._assert_connection()
        callback = await self.message_callbacks.get()
        response = callback(message)
        await self.messages.put(response)
        await asyncio.sleep(0)

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

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.receive()

    @classmethod
    def of(cls, connection: AsyncScConnection) -> WebsocketStub:
        # noinspection PyProtectedMember
        # pylint: disable=protected-access
        return connection._websocket

    async def set_message_callback(self, callback: Callable[[str], str]) -> None:
        await self.message_callbacks.put(callback)

    class lose_connection:
        """Context manager to lose and establish connection"""

        async def __aenter__(self):
            WebsocketStub.is_connection_lost = True
            await asyncio.sleep(0)

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            WebsocketStub.is_connection_lost = False
            await asyncio.sleep(0)


async def sc_connect_patch(url: str) -> WebsocketStub:
    websocket_mock = WebsocketStub()
    await websocket_mock.connect(url)
    return websocket_mock
