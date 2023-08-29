import asyncio
import json
import logging
from typing import Dict
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from sc_client.constants import common
from sc_client.constants.common import RequestType
from sc_client.core.async_sc_connection import AsyncScConnection
from sc_client.models import Response
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
        await connection.disconnect()

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
                async with websocket.lose_connection():
                    exception = task.exception()
                    self.assertIsInstance(exception, ScServerError)
                    self.assertIn(ErrorNotes.CONNECTION_TO_SC_SERVER_LOST, exception.args[0])
                    break
        else:
            raise AssertionError("Task 'Handle messages' wasn't found")

    async def test_send_receive(self):
        connection = AsyncScConnection()
        await connection.connect("url")
        websocket = WebsocketStub.of(connection)
        request_type = RequestType.CHECK_ELEMENTS
        payload = [1, 2]

        def callback(message_json: str) -> str:
            message: Dict[str, any] = json.loads(message_json)
            return Response(message[common.ID], True, False, "[3, 4]", None).dump()

        await websocket.set_message_callback(callback)
        response = await connection.send_message(request_type, payload)
        self.assertEqual(response.payload, "[3, 4]")

    async def test_sc_server_doesnt_response(self):
        connection = AsyncScConnection()
        connection.reconnect_retries = 1
        connection.reconnect_delay = 0
        await connection.connect("url")
        websocket = WebsocketStub.of(connection)
        async with websocket.lose_connection():
            with self.assertRaisesRegex(ScServerError, ErrorNotes.SC_SERVER_TAKES_A_LONG_TIME_TO_RESPOND):
                await connection.send_message(RequestType.CHECK_ELEMENTS, None)
