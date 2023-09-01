import logging
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from sc_client import ScAddr, ScConstruction, ScLinkContent, ScLinkContentType, ScType
from sc_client.constants import common, sc_types
from sc_client.constants.common import RequestType
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


class CheckElementsTestCase(AsyncScClientActionsTestCase):
    async def test_ok(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert payload_ == [1, 2]
                assert type_ == common.RequestType.CHECK_ELEMENTS
                return Response(id_, True, False, [11, 22], None)

        await self.websocket.set_message_callback(Callback())
        result = await self.client.check_elements(ScAddr(1), ScAddr(2))
        self.assertEqual(result, [ScType(11), ScType(22)])

    async def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR):
            # noinspection PyTypeChecker
            await self.client.check_elements(1, 2)

    async def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        await self.websocket.set_message_callback(NoRunCallback())
        result = await self.client.check_elements()
        self.assertEqual(result, [])


class DeleteElementsTestCase(AsyncScClientActionsTestCase):
    async def test_ok(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert payload_ == [1, 2]
                assert type_ == common.RequestType.DELETE_ELEMENTS
                return Response(id_, True, False, [1], [])

        await self.websocket.set_message_callback(Callback())
        result = await self.client.delete_elements(ScAddr(1), ScAddr(2))
        self.assertTrue(result)

    async def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR):
            # noinspection PyTypeChecker
            await self.client.delete_elements(1, 2)

    async def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        await self.websocket.set_message_callback(NoRunCallback())
        result = await self.client.delete_elements()
        self.assertTrue(result)


class CreateElementsTestCase(AsyncScClientActionsTestCase):
    async def test_ok(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert payload_ == [
                    {common.ELEMENT: common.Elements.NODE, common.TYPE: sc_types.NODE_CONST.value},
                    {
                        common.CONTENT: "link content",
                        common.CONTENT_TYPE: ScLinkContentType.STRING.value,
                        common.ELEMENT: common.Elements.LINK,
                        common.TYPE: sc_types.LINK_CONST.value,
                    },
                    {
                        common.ELEMENT: common.Elements.EDGE,
                        common.SOURCE: {common.TYPE: common.REF, common.VALUE: 0},
                        common.TARGET: {common.TYPE: common.REF, common.VALUE: 1},
                        common.TYPE: sc_types.EDGE_ACCESS_CONST_POS_PERM.value,
                    },
                ]
                assert type_ == common.RequestType.CREATE_ELEMENTS
                return Response(id_, True, False, [1, 2, 3], [])

        await self.websocket.set_message_callback(Callback())
        construction = ScConstruction()
        construction.create_node(sc_types.NODE_CONST, alias="node_src")
        construction.create_link(
            sc_types.LINK_CONST, ScLinkContent("link content", ScLinkContentType.STRING), alias="link_trg"
        )
        construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, src="node_src", trg="link_trg")
        addrs = await self.client.create_elements(construction)
        self.assertEqual(len(addrs), 3)
        self.assertEqual(addrs, [ScAddr(1), ScAddr(2), ScAddr(3)])

    async def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScConstruction")):
            # noinspection PyTypeChecker
            await self.client.create_elements("fake_construction")

    async def test_empty_construction(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        await self.websocket.set_message_callback(NoRunCallback())
        construction = ScConstruction()
        result = await self.client.create_elements(construction)
        self.assertEqual(result, [])


class CreateElementsBySCsTestCase(AsyncScClientActionsTestCase):
    async def test_ok(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == RequestType.CREATE_ELEMENTS_BY_SCS
                assert payload_ == [
                    {common.OUTPUT_STRUCTURE: 0, common.SCS: "concept1 -> node1;;"},
                    {common.OUTPUT_STRUCTURE: 0, common.SCS: "concept2 -> node2;;"},
                ]
                return Response(id_, True, False, [1, 2], [])

        await self.websocket.set_message_callback(Callback())
        addrs = await self.client.create_elements_by_scs(["concept1 -> node1;;", "concept2 -> node2;;"])
        self.assertEqual(addrs, [True, True])

    async def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("string or SCs")):
            # noinspection PyTypeChecker
            await self.client.create_elements_by_scs("wrong type here")
            # noinspection PyTypeChecker
            await self.client.create_elements_by_scs([1])

    async def test_error_params(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                # pylint: disable=unused-argument
                return Response(id_, False, False, [0], [{"message": "Parse error ...", "ref": 0}])

        await self.websocket.set_message_callback(Callback())
        with self.assertRaisesRegex(ScServerError, ErrorNotes.GOT_ERROR.format("Parse error ...")):
            await self.client.create_elements_by_scs(["concept1 -> ;;"])

    async def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        await self.websocket.set_message_callback(NoRunCallback())
        result = await self.client.create_elements_by_scs([])
        self.assertEqual(result, [])


class GetLinksContentTestCase(AsyncScClientActionsTestCase):
    async def test_ok(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == RequestType.CONTENT
                assert payload_ == [
                    {common.ADDR: 1, common.COMMAND: common.CommandTypes.GET},
                    {common.ADDR: 2, common.COMMAND: common.CommandTypes.GET},
                    {common.ADDR: 3, common.COMMAND: common.CommandTypes.GET},
                ]
                payload_response = [
                    {common.TYPE: ScLinkContentType.STRING.name.lower(), common.VALUE: "str1"},
                    {common.TYPE: ScLinkContentType.INT.name.lower(), common.VALUE: 1},
                    {common.TYPE: ScLinkContentType.FLOAT.name.lower(), common.VALUE: 1.0},
                ]
                return Response(id_, True, False, payload_response, [])

        await self.websocket.set_message_callback(Callback())
        contents_received = await self.client.get_link_content(ScAddr(1), ScAddr(2), ScAddr(3))
        self.assertEqual(
            contents_received,
            [
                ScLinkContent("str1", content_type=ScLinkContentType.STRING),
                ScLinkContent(1, content_type=ScLinkContentType.INT),
                ScLinkContent(1.0, content_type=ScLinkContentType.FLOAT),
            ],
        )

    async def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR):
            # noinspection PyTypeChecker
            await self.client.get_link_content(12)

    async def test_error_params(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                # pylint: disable=unused-argument
                return Response(id_, False, False, None, "Invalid state ...")

        await self.websocket.set_message_callback(Callback())
        with self.assertRaisesRegex(ScServerError, ErrorNotes.GOT_ERROR.format("Invalid state ...")):
            await self.client.get_link_content(ScAddr(111222))

    async def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        await self.websocket.set_message_callback(NoRunCallback())
        result = await self.client.get_link_content()
        self.assertEqual(result, [])


class SetLinksContentTestCase(AsyncScClientActionsTestCase):
    # async def test_ok(self):
    #     class Callback(ResponseCallback):
    #         def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
    #             assert type_ == RequestType.CREATE_ELEMENTS_BY_SCS
    #             assert payload_ == [...]
    #             return Response(id_, True, False, [1], [])
    #
    #     await self.websocket.set_message_callback(Callback())
    #     contents = [
    #         ScLinkContent("str", content_type=ScLinkContentType.STRING),
    #         ScLinkContent(2, content_type=ScLinkContentType.INT),
    #         ScLinkContent(3.0, content_type=ScLinkContentType.FLOAT),
    #     ]
    #     addrs = await self.client.set_link_contents(*contents)
    #     self.assertTrue(addrs)

    async def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScLinkContent")):
            # noinspection PyTypeChecker
            await self.client.set_link_contents("wrong type here")

    # async def test_error_params(self):
    #     class Callback(ResponseCallback):
    #         def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
    #             # pylint: disable=unused-argument
    #             return Response(id_, False, False, [0], [{"message": "Parse error ...", "ref": 0}])
    #
    #     await self.websocket.set_message_callback(Callback())
    #     with self.assertRaisesRegex(ScServerError, ErrorNotes.GOT_ERROR.format(repr("Parse error ..."))):
    #         await self.client.create_elements_by_scs(["concept1 -> ;;"])

    async def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        await self.websocket.set_message_callback(NoRunCallback())
        result = await self.client.set_link_contents()
        self.assertTrue(result)
