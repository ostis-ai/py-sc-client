from typing import Any
from unittest import TestCase
from unittest.mock import patch

from sc_client import ScAddr, ScType
from sc_client.constants import common
from sc_client.core import ScClient
from sc_client.core.response import Response
from sc_client.testing import ResponseCallback, SimpleResponseCallback, WebsocketStub, websockets_client_connect_patch


@patch("websockets.client.connect", websockets_client_connect_patch)
class ScClientTestCase(TestCase):
    def test_connection(self) -> None:
        client = ScClient()
        client.connect("url")
        self.assertTrue(client.is_connected())
        client.disconnect()
        self.assertFalse(client.is_connected())


class ScClientActionsTestCase(TestCase):
    client: ScClient
    websocket: WebsocketStub

    @patch("websockets.client.connect", websockets_client_connect_patch)
    def setUp(self) -> None:
        self.client = ScClient()
        self.client.connect("url")
        self.websocket = WebsocketStub.of(self.client)

    def tearDown(self) -> None:
        self.client.disconnect()

    def test_someting(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert payload_ == [1, 2]
                assert type_ == common.RequestType.CHECK_ELEMENTS
                return Response(id_, True, False, [11, 22], None)

        self.websocket.sync_set_message_callback(Callback())
        result = self.client.check_elements(ScAddr(1), ScAddr(2))
        self.assertEqual(result, [ScType(11), ScType(22)])

    def test_something_simpler(self):
        self.websocket.sync_set_message_callback(SimpleResponseCallback(True, False, [11, 22], None))
        result = self.client.check_elements(ScAddr(1), ScAddr(2))
        self.assertEqual(result, [ScType(11), ScType(22)])
