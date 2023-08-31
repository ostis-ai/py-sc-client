import logging
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from sc_client import ScAddr, ScType
from sc_client.constants import common
from sc_client.core import AsyncScClient
from sc_client.models import Response
from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError, ScServerError
from sc_client.testing import ResponseCallback, WebsocketStub, websockets_client_connect_patch

logging.basicConfig(level=logging.DEBUG, force=True, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


@patch("websockets.client.connect", websockets_client_connect_patch)
class AsyncScClientTestCase(IsolatedAsyncioTestCase):
    async def test_connection(self) -> None:
        client = AsyncScClient()
        await client.connect("url")
        self.assertTrue(client.is_connected())
        await client.disconnect()
        self.assertFalse(client.is_connected())

    async def test_wrong_connection(self):
        client = AsyncScClient()
        with self.assertRaisesRegex(ScServerError, ErrorNotes.CANNOT_CONNECT_TO_SC_SERVER):
            await client.connect("")
        self.assertFalse(client.is_connected())


class AsyncScClientActionsTestCase(IsolatedAsyncioTestCase):
    client: AsyncScClient
    websocket: WebsocketStub

    @patch("websockets.client.connect", websockets_client_connect_patch)
    async def asyncSetUp(self) -> None:
        self.client = AsyncScClient()
        await self.client.connect("url")
        self.websocket = WebsocketStub.of(self.client)

    async def asyncTearDown(self) -> None:
        await self.client.disconnect()

    async def test_check_elements(self):
        addr1, addr2 = ScAddr(1), ScAddr(2)
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR):
            # noinspection PyTypeChecker
            await self.client.check_elements(1, 2)

        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert payload_ == [1, 2]
                assert type_ == common.RequestType.CHECK_ELEMENTS
                return Response(id_, True, False, [11, 22], None)

        callback = Callback()
        await self.websocket.set_message_callback(callback)
        result = await self.client.check_elements(addr1, addr2)
        self.assertEqual(result, [ScType(11), ScType(22)])
