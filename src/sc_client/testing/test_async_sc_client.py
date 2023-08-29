import asyncio
import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from sc_client.core import AsyncScClient
from sc_client.testing.websocket_stub import sc_connect_patch

logging.basicConfig(level=logging.DEBUG, force=True, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


@patch("websockets.client.connect", sc_connect_patch)
class AsyncScClientMockTestCase(IsolatedAsyncioTestCase):
    async def test_sc_client(self) -> None:
        client = AsyncScClient()
        await client.connect("url")
        await asyncio.sleep(0.1)
        await client.disconnect()
