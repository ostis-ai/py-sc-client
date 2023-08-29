import asyncio
import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from sc_client.core.async_sc_connection import AsyncScConnection
from sc_client.sc_exceptions import ErrorNotes, ScServerError
from sc_client.testing.websocket_stub import WebsocketStub, sc_connect_patch

logging.basicConfig(level=logging.DEBUG, force=True, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


@patch("websockets.client.connect", sc_connect_patch)
class AsyncScConnectionTestCase(IsolatedAsyncioTestCase):
    async def test_connection(self):
        connection = AsyncScConnection()
        await connection.connect("url")
        self.assertTrue(connection.is_connected())
        await connection.disconnect()
        self.assertFalse(connection.is_connected())

    async def test_wrong_connection(self):
        connection = AsyncScConnection()
        with self.assertRaisesRegex(ScServerError, ErrorNotes.CANNOT_CONNECT_TO_SC_SERVER):
            await connection.connect("")

    async def test_lose_connection(self):
        connection = AsyncScConnection()
        await connection.connect("url")
        self.assertTrue(connection.is_connected())
        websocket = WebsocketStub.of(connection)
        for task in asyncio.all_tasks():
            if task.get_name() == "Handle messages":
                await websocket.lose_connection()
                exception = task.exception()
                self.assertIsInstance(exception, ScServerError)
                self.assertIn(ErrorNotes.CONNECTION_TO_SC_SERVER_LOST, exception.args[0])
                break
        else:
            raise AssertionError("Task 'Handle messages' wasn't found")
