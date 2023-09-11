from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from sc_client import ScAddr, ScType
from sc_client.constants import common
from sc_client.core import AsyncScClient
from sc_client.models import Response
from sc_client.testing import ResponseCallback, SimpleResponseCallback, WebsocketStub, websockets_client_connect_patch


@patch("websockets.client.connect", websockets_client_connect_patch)
class AsyncScClientTestCase(IsolatedAsyncioTestCase):
    async def test_connection(self) -> None:
        client = AsyncScClient()
        await client.connect("url")
        self.assertTrue(client.is_connected())
        await client.disconnect()
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

    async def test_someting(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert payload_ == [1, 2]
                assert type_ == common.RequestType.CHECK_ELEMENTS
                return Response(id_, True, False, [11, 22], None)

        await self.websocket.set_message_callback(Callback())
        result = await self.client.check_elements(ScAddr(1), ScAddr(2))
        self.assertEqual(result, [ScType(11), ScType(22)])

    async def test_something_simpler(self):
        await self.websocket.set_message_callback(SimpleResponseCallback(True, False, [11, 22], None))
        result = await self.client.check_elements(ScAddr(1), ScAddr(2))
        self.assertEqual(result, [ScType(11), ScType(22)])
