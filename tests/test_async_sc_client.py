import asyncio
import logging
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from sc_client import ScAddr, ScConstruction, ScLinkContent, ScLinkContentType, ScTemplate, ScType
from sc_client.constants import common, sc_types
from sc_client.constants.common import RequestType, ScEventType
from sc_client.core import AScClient
from sc_client.core.response import Response
from sc_client.models import AScEventParams, ScIdtfResolveParams
from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError, ScServerError
from sc_client.testing import ResponseCallback, SimpleResponseCallback, WebsocketStub, websockets_client_connect_patch

logging.basicConfig(level=logging.DEBUG, force=True, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


@patch("websockets.client.connect", websockets_client_connect_patch)
class AsyncScClientTestCase(IsolatedAsyncioTestCase):
    async def test_connection(self) -> None:
        client = AScClient()
        await client.connect("url")
        self.assertTrue(client.is_connected())
        await client.disconnect()
        self.assertFalse(client.is_connected())

    async def test_wrong_connection(self):
        client = AScClient()
        with self.assertRaisesRegex(ScServerError, ErrorNotes.CANNOT_CONNECT_TO_SC_SERVER):
            await client.connect("")
        self.assertFalse(client.is_connected())


class AsyncScClientActionsTestCase(IsolatedAsyncioTestCase):
    client: AScClient
    websocket: WebsocketStub

    @patch("websockets.client.connect", websockets_client_connect_patch)
    async def asyncSetUp(self) -> None:
        self.client = AScClient()
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
    async def test_ok(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == RequestType.CONTENT
                assert payload_ == [
                    {
                        common.ADDR: 1,
                        common.COMMAND: common.CommandTypes.SET,
                        common.TYPE: ScLinkContentType.STRING.name.lower(),
                        common.DATA: "str",
                    },
                    {
                        common.ADDR: 2,
                        common.COMMAND: common.CommandTypes.SET,
                        common.TYPE: ScLinkContentType.INT.name.lower(),
                        common.DATA: 2,
                    },
                    {
                        common.ADDR: 3,
                        common.COMMAND: common.CommandTypes.SET,
                        common.TYPE: ScLinkContentType.FLOAT.name.lower(),
                        common.DATA: 3.0,
                    },
                ]
                return Response(id_, True, False, None, [])

        await self.websocket.set_message_callback(Callback())
        addrs = await self.client.set_link_contents(
            ScLinkContent("str", ScLinkContentType.STRING, ScAddr(1)),
            ScLinkContent(2, ScLinkContentType.INT, ScAddr(2)),
            ScLinkContent(3.0, ScLinkContentType.FLOAT, ScAddr(3)),
        )
        self.assertTrue(addrs)

    async def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScLinkContent")):
            # noinspection PyTypeChecker
            await self.client.set_link_contents("wrong type here")

    async def test_error_params(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                # pylint: disable=unused-argument
                return Response(id_, False, False, [0], [{"message": "Some error on sc-server ....", "ref": 0}])

        await self.websocket.set_message_callback(Callback())
        with self.assertRaisesRegex(ScServerError, ErrorNotes.GOT_ERROR.format("Some error on sc-server ....")):
            await self.client.set_link_contents(ScLinkContent("str", ScLinkContentType.INT, ScAddr(1)))

    async def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        await self.websocket.set_message_callback(NoRunCallback())
        result = await self.client.set_link_contents()
        self.assertTrue(result)


class GetLinksTestCase(AsyncScClientActionsTestCase):
    params = [
        (AScClient.get_links_by_content, common.CommandTypes.FIND),
        (AScClient.get_links_by_content_substring, common.CommandTypes.FIND_LINKS_BY_SUBSTRING),
        (
            AScClient.get_links_contents_by_content_substring,
            common.CommandTypes.FIND_LINKS_CONTENTS_BY_CONTENT_SUBSTRING,
        ),
    ]

    async def test_ok(self):
        for method, command in self.params:
            # pylint: disable=cell-var-from-loop
            class Callback(ResponseCallback):
                def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                    assert type_ == RequestType.CONTENT
                    assert payload_ == [
                        {common.COMMAND: command, common.DATA: data} for data in ("str_content", "str", 12, 3.14)
                    ]
                    return Response(id_, True, False, [[1], [2, 3]], None)

            await self.websocket.set_message_callback(Callback())
            contents = [ScLinkContent("str_content", ScLinkContentType.STRING), "str", 12, 3.14]
            await method(self.client, *contents)

    async def test_wrong_params(self):
        for method, _ in self.params:
            with self.assertRaisesRegex(
                InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScLinkContent, str, int or float")
            ):
                # noinspection PyTypeChecker
                await method(self.client, ("wrong type here",))

    async def test_error_params(self):
        for method, _ in self.params:

            class Callback(ResponseCallback):
                def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                    # pylint: disable=unused-argument
                    return Response(id_, False, False, [0], [{"message": "Some error on sc-server ....", "ref": 0}])

            await self.websocket.set_message_callback(Callback())
            with self.assertRaisesRegex(ScServerError, ErrorNotes.GOT_ERROR.format("Some error on sc-server ....")):
                await method(self.client, ScLinkContent("str", ScLinkContentType.INT))

    async def test_empty_params(self):
        for method, _ in self.params:

            class NoRunCallback(ResponseCallback):
                def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                    raise AssertionError

            await self.websocket.set_message_callback(NoRunCallback())
            result = await method(self.client)
            self.assertEqual(result, [])


class ResolveKeynodesTestCase(AsyncScClientActionsTestCase):
    async def test_ok(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == common.RequestType.KEYNODES
                assert payload_ == [
                    {
                        common.COMMAND: common.CommandTypes.RESOLVE,
                        common.ELEMENT_TYPE: sc_types.NODE_CONST_CLASS.value,
                        common.IDTF: "some_class",
                    },
                    {
                        common.COMMAND: common.CommandTypes.RESOLVE,
                        common.ELEMENT_TYPE: sc_types.NODE_CONST.value,
                        common.IDTF: "some_node",
                    },
                    {
                        common.COMMAND: common.CommandTypes.FIND,
                        common.IDTF: "some_existing_element",
                    },
                ]
                return Response(id_, True, False, [1, 2], None)

        await self.websocket.set_message_callback(Callback())
        params = [
            ScIdtfResolveParams("some_class", sc_types.NODE_CONST_CLASS),
            ScIdtfResolveParams("some_node", sc_types.NODE_CONST),
            ScIdtfResolveParams("some_existing_element", None),
        ]
        await self.client.resolve_keynodes(*params)

    async def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScIdtfResolveParams")):
            await self.client.resolve_keynodes(sc_types.NODE_CONST)

    async def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        await self.websocket.set_message_callback(NoRunCallback())
        result = await self.client.resolve_keynodes()
        self.assertEqual(result, [])


class TemplateTestCase(AsyncScClientActionsTestCase):
    async def test_ok_search_sc_template(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == common.RequestType.SEARCH_TEMPLATE
                assert payload_ == {
                    common.TEMPLATE: [
                        [
                            {common.TYPE: common.ADDR, common.VALUE: 1},
                            {
                                common.TYPE: common.TYPE,
                                common.VALUE: sc_types.EDGE_ACCESS_VAR_POS_PERM.value,
                                common.ALIAS: "edge",
                            },
                            {common.TYPE: common.TYPE, common.VALUE: sc_types.NODE_VAR.value},
                        ]
                    ],
                    common.PARAMS: {},
                }
                return Response(id_, True, False, {common.ALIASES: {"edge": 2}, common.ADDRS: [[1, 2, 3]]}, None)

        await self.websocket.set_message_callback(Callback())
        template = ScTemplate().triple(ScAddr(1), sc_types.EDGE_ACCESS_VAR_POS_PERM >> "edge", sc_types.NODE_VAR)
        result = (await self.client.template_search(template))[0]
        self.assertEqual(result.addrs, [ScAddr(1), ScAddr(2), ScAddr(3)])
        self.assertEqual(result.aliases, {"edge": 2})

    async def test_ok_generate_sc_template(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == common.RequestType.GENERATE_TEMPLATE
                assert payload_ == {
                    common.TEMPLATE: [
                        [
                            {common.TYPE: common.ADDR, common.VALUE: 1},
                            {
                                common.TYPE: common.TYPE,
                                common.VALUE: sc_types.EDGE_ACCESS_VAR_POS_PERM.value,
                                common.ALIAS: "edge",
                            },
                            {common.TYPE: common.ADDR, common.VALUE: 3},
                        ]
                    ],
                    common.PARAMS: {},
                }
                return Response(id_, True, False, {common.ALIASES: {"edge": 2}, common.ADDRS: [1, 2, 3]}, None)

        await self.websocket.set_message_callback(Callback())
        template = ScTemplate().triple(ScAddr(1), sc_types.EDGE_ACCESS_VAR_POS_PERM >> "edge", ScAddr(3))
        result = await self.client.template_generate(template)
        self.assertEqual(result.addrs, [ScAddr(1), ScAddr(2), ScAddr(3)])
        self.assertEqual(result.aliases, {"edge": 2})

    async def test_ok_search_scs_template(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == common.RequestType.SEARCH_TEMPLATE
                assert payload_ == {
                    common.TEMPLATE: {
                        common.TYPE: common.IDTF,
                        common.VALUE: "person _-> .._p (* _=> nrel_email:: _[test@email.com] *);;",
                    },
                    common.PARAMS: {".._p": 5314},
                }
                return Response(id_, True, False, {common.ALIASES: {}, common.ADDRS: []}, None)

        await self.websocket.set_message_callback(Callback())
        template = "person _-> .._p (* _=> nrel_email:: _[test@email.com] *);;"
        params = {".._p": ScAddr(5314)}
        results = await self.client.template_search(template, params)
        self.assertEqual(results, [])

    # noinspection PyTypeChecker
    async def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScTemplate")):
            await self.client.template_search(None)
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScTemplate")):
            await self.client.template_generate(None)

    async def test_wrong_template(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.VAR_TYPE_IN_TEMPLATE):
            ScTemplate().triple(ScAddr(0), sc_types.EDGE_ACCESS_CONST_POS_PERM, ScAddr(0))


class ScEventsTestCase(AsyncScClientActionsTestCase):
    async def test_ok_create_and_destroy(self):
        async def test_callback(*_):
            pass

        param = AScEventParams(ScAddr(12), ScEventType.ADD_OUTGOING_EDGE, test_callback)

        class CreateCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == common.RequestType.EVENTS
                nonlocal param
                assert payload_ == {
                    common.CommandTypes.CREATE: [{common.TYPE: param.event_type.value, common.ADDR: param.addr.value}]
                }
                return Response(id_, True, False, [1], None)

        await self.websocket.set_message_callback(CreateCallback())
        events = await self.client.events_create(param)
        self.assertTrue(self.client.is_event_valid(events[0]))

        class DestroyCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == common.RequestType.EVENTS
                nonlocal events
                assert payload_ == {common.CommandTypes.DELETE: [event.id for event in events]}
                return Response(id_, True, False, None, None)

        await self.websocket.set_message_callback(DestroyCallback())
        is_event_deleted = await self.client.events_destroy(*events)
        self.assertTrue(is_event_deleted)
        self.assertFalse(self.client.is_event_valid(events[0]))

    async def test_ok_create_and_run_event(self):
        async def test_callback(src: ScAddr, *_):
            nonlocal is_call_succesfull
            is_call_succesfull = src == ScAddr(12)

        is_call_succesfull = False
        await self.websocket.set_message_callback(SimpleResponseCallback(True, False, [1], None))
        events = await self.client.events_create(
            AScEventParams(ScAddr(12), ScEventType.ADD_OUTGOING_EDGE, test_callback)
        )
        await self.websocket.messages.put(
            f'{{"id": {events[0].id}, "event": true, "status": true, "payload": [12, 0, 0], "errors": []}}'
        )
        await asyncio.sleep(0.001)
        assert is_call_succesfull

    async def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("AsyncScEventParams")):
            await self.client.events_create("wrong type here")

    async def test_is_event_valid_incorrect_arguments(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("AsyncScEvent")):
            self.client.is_event_valid("wrong type here")

    async def test_events_destroy_incorrect_arguments(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("AsyncScEvent")):
            await self.client.events_destroy("wrong type here")
