from __future__ import annotations

import asyncio
import logging

from websockets.exceptions import ConnectionClosed, ConnectionClosedOK

from sc_client.core.async_sc_connection import AsyncScConnection


class WebsocketStub:
    """Stub for async websockets.client.WebSocketClientProtocol"""

    def __init__(self, *args: any, **kwargs: any):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.is_connected = False
        self.messages = asyncio.Queue()

    @classmethod
    def of(cls, connection: AsyncScConnection) -> WebsocketStub:
        # noinspection PyProtectedMember
        # pylint: disable=protected-access
        return connection._websocket

    async def connect(self, url: str):
        await asyncio.sleep(0.01)
        if not url:
            raise ConnectionRefusedError
        self.logger.info("Mock connection")
        self.is_connected = True

    async def close(self):
        await asyncio.sleep(0.01)
        self.logger.info("Mock disonnection")
        self.is_connected = False
        await self.messages.put(1)
        # await self.messages.join()

    @property
    def open(self) -> bool:
        return self.is_connected

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def __aiter__(self):
        return self

    async def __anext__(self):
        message = await self.messages.get()
        if not isinstance(message, int):
            return message
        # 1: OK, 2: Lose connection, 3: Other errors
        if message == 1:
            raise ConnectionClosedOK(None, None)
        if message == 2:
            raise ConnectionClosed(None, None)
        if message == 3:
            raise Exception

    async def lose_connection(self):
        self.is_connected = False
        await self.messages.put(2)
        await asyncio.sleep(0)


async def sc_connect_patch(url: str) -> WebsocketStub:
    websocket_mock = WebsocketStub()
    await websocket_mock.connect(url)
    return websocket_mock
