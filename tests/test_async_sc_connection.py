import asyncio
import logging
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from sc_client import ScAddr
from sc_client.constants import common
from sc_client.constants.common import RequestType, ScEventType
from sc_client.constants.config import MAX_PAYLOAD_SIZE
from sc_client.core.asc_connection import AScConnection
from sc_client.core.response import Response
from sc_client.models import AScEvent
from sc_client.sc_exceptions import ErrorNotes, PayloadMaxSizeError, ScServerError
from sc_client.testing import ResponseCallback, WebsocketStub, websockets_client_connect_patch

logging.basicConfig(level=logging.DEBUG, force=True, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


@patch("websockets.client.connect", websockets_client_connect_patch)
class AsyncScConnectionTestCase(IsolatedAsyncioTestCase):
    async def test_connection(self):
        connection = AScConnection()
        await connection.connect("url")
        self.assertTrue(connection.is_connected())
        await connection.disconnect()
        self.assertFalse(connection.is_connected())
        await connection.disconnect()

    async def test_wrong_connection(self):
        connection = AScConnection()
        with self.assertRaisesRegex(ScServerError, ErrorNotes.CANNOT_CONNECT_TO_SC_SERVER):
            await connection.connect("")
        self.assertFalse(connection.is_connected())

    async def test_lose_connection(self):
        connection = AScConnection()
        await connection.connect("url")
        self.assertTrue(connection.is_connected())
        websocket = WebsocketStub.of(connection)
        for task in asyncio.all_tasks():
            if task.get_name() == "Handle messages":
                async with websocket.lose_connection():
                    self.assertIsNone(task.result())
                    break
        else:
            raise AssertionError("Task 'Handle messages' wasn't found")
        await connection.disconnect()

    async def test_send_receive(self):
        connection = AScConnection()
        await connection.connect("url")
        websocket = WebsocketStub.of(connection)
        request_type = RequestType.CHECK_ELEMENTS
        payload = [1, 2]

        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                return Response(id_, True, False, "test_send_receive", None)

        await websocket.set_message_callback(Callback())
        response = await connection.send_message(request_type, payload)
        self.assertEqual(response.payload, "test_send_receive")
        await connection.disconnect()
        with self.assertRaisesRegex(ScServerError, ErrorNotes.ALREADY_DISCONNECTED):
            await connection.send_message(request_type, payload)
        await connection.disconnect()

    async def test_sc_server_doesnt_response(self):
        connection = AScConnection()
        connection.reconnect_retries = 1
        connection.reconnect_delay = 0
        await connection.connect("url")
        websocket = WebsocketStub.of(connection)
        async with websocket.lose_connection():
            with self.assertRaisesRegex(ScServerError, ErrorNotes.SC_SERVER_TAKES_A_LONG_TIME_TO_RESPOND):
                await connection.send_message(RequestType.CHECK_ELEMENTS, None)
        await connection.disconnect()

    async def test_reconnect(self):
        connection = AScConnection()
        connection.reconnect_retries = 5
        connection.reconnect_delay = 0.1
        await connection.connect("url")
        websocket = WebsocketStub.of(connection)
        request_type = RequestType.CHECK_ELEMENTS
        payload = 1

        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                return Response(id_, True, False, "2", None)

        await websocket.set_message_callback(Callback())
        send_message_coroutine = connection.send_message(request_type, payload)

        async with websocket.lose_connection():
            task = asyncio.create_task(send_message_coroutine)
            await asyncio.sleep(connection.reconnect_delay)
        await task
        response = task.result()
        self.assertEqual(response.payload, "2")
        await connection.disconnect()

    async def test_lose_connection_while_receiving(self):
        connection = AScConnection()
        connection.reconnect_retries = 5
        connection.reconnect_delay = 0.1
        await connection.connect("url")
        websocket = WebsocketStub.of(connection)

        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                return Response(id_, True, False, "2", None)

        await websocket.set_message_callback(Callback(0.02))
        send_message_coroutine = connection.send_message(RequestType.CHECK_ELEMENTS, None)
        task = asyncio.create_task(send_message_coroutine)
        await asyncio.sleep(0.01)
        async with websocket.lose_connection():
            with self.assertRaisesRegex(ScServerError, ErrorNotes.CONNECTION_TO_SC_SERVER_LOST):
                await asyncio.sleep(0.02)
                await task  # Lose connection after sending and before receiving
        await connection.disconnect()

    async def test_payload_max_size(self):
        connection = AScConnection()
        await connection.connect("url")
        with self.assertRaises(PayloadMaxSizeError):
            await connection.send_message(RequestType.CHECK_ELEMENTS, "0" * (MAX_PAYLOAD_SIZE + 1))
        await connection.disconnect()

    async def test_event(self):
        connection = AScConnection()
        await connection.connect("url")
        websocket = WebsocketStub.of(connection)

        event_run_times = 0

        async def event_callback(*params: ScAddr) -> None:
            self.assertEqual(params, (ScAddr(1), ScAddr(2), ScAddr(3)))
            nonlocal event_run_times
            event_run_times += 1

        event = AScEvent(20, ScEventType.ADD_OUTGOING_EDGE, event_callback)
        connection.set_event(event)
        event_same = connection.get_event(20)
        await websocket.messages.put(Response(20, True, True, [1, 2, 3], None).dump())
        await asyncio.sleep(0)
        self.assertEqual(event, event_same)
        connection.drop_event(20)
        await websocket.messages.put(Response(20, True, True, [4, 5, 6], None).dump())
        await asyncio.sleep(0)
        self.assertEqual(event_run_times, 1)
        await connection.disconnect()
