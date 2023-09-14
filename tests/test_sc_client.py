import asyncio
import logging
from typing import Any
from unittest import TestCase
from unittest.mock import patch

from sc_client import ScAddr, ScConstruction, ScEventParams, ScLinkContent, ScLinkContentType, ScTemplate, ScType
from sc_client.constants import common, sc_types
from sc_client.constants.common import RequestType, ScEventType
from sc_client.core import ScClient
from sc_client.core.response import Response
from sc_client.models import ScIdtfResolveParams
from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError, ScServerError
from sc_client.testing import ResponseCallback, SimpleResponseCallback, WebsocketStub, websockets_client_connect_patch

logging.basicConfig(level=logging.DEBUG, force=True, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


@patch("websockets.client.connect", websockets_client_connect_patch)
class ScClientTestCase(TestCase):
    def test_connection(self) -> None:
        client = ScClient()
        client.connect("url")
        self.assertTrue(client.is_connected())
        client.disconnect()
        self.assertFalse(client.is_connected())

    def test_wrong_connection(self):
        client = ScClient()
        with self.assertRaisesRegex(ScServerError, ErrorNotes.CANNOT_CONNECT_TO_SC_SERVER):
            client.connect("")
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


class CheckElementsTestCase(ScClientActionsTestCase):
    def test_ok(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert payload_ == [1, 2]
                assert type_ == common.RequestType.CHECK_ELEMENTS
                return Response(id_, True, False, [11, 22], None)

        self.websocket.sync_set_message_callback(Callback())
        result = self.client.check_elements(ScAddr(1), ScAddr(2))
        self.assertEqual(result, [ScType(11), ScType(22)])

    def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR):
            # noinspection PyTypeChecker
            self.client.check_elements(1, 2)

    def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        self.websocket.sync_set_message_callback(NoRunCallback())
        result = self.client.check_elements()
        self.assertEqual(result, [])


class DeleteElementsTestCase(ScClientActionsTestCase):
    def test_ok(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert payload_ == [1, 2]
                assert type_ == common.RequestType.DELETE_ELEMENTS
                return Response(id_, True, False, [1], [])

        self.websocket.sync_set_message_callback(Callback())
        result = self.client.delete_elements(ScAddr(1), ScAddr(2))
        self.assertTrue(result)

    def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR):
            # noinspection PyTypeChecker
            self.client.delete_elements(1, 2)

    def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        self.websocket.sync_set_message_callback(NoRunCallback())
        result = self.client.delete_elements()
        self.assertTrue(result)


class CreateElementsTestCase(ScClientActionsTestCase):
    def test_ok(self):
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

        self.websocket.sync_set_message_callback(Callback())
        construction = ScConstruction()
        construction.create_node(sc_types.NODE_CONST, alias="node_src")
        construction.create_link(
            sc_types.LINK_CONST, ScLinkContent("link content", ScLinkContentType.STRING), alias="link_trg"
        )
        construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, src="node_src", trg="link_trg")
        addrs = self.client.create_elements(construction)
        self.assertEqual(len(addrs), 3)
        self.assertEqual(addrs, [ScAddr(1), ScAddr(2), ScAddr(3)])

    def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScConstruction")):
            # noinspection PyTypeChecker
            self.client.create_elements("fake_construction")

    def test_empty_construction(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        self.websocket.sync_set_message_callback(NoRunCallback())
        construction = ScConstruction()
        result = self.client.create_elements(construction)
        self.assertEqual(result, [])


class CreateElementsBySCsTestCase(ScClientActionsTestCase):
    def test_ok(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == RequestType.CREATE_ELEMENTS_BY_SCS
                assert payload_ == [
                    {common.OUTPUT_STRUCTURE: 0, common.SCS: "concept1 -> node1;;"},
                    {common.OUTPUT_STRUCTURE: 0, common.SCS: "concept2 -> node2;;"},
                ]
                return Response(id_, True, False, [1, 2], [])

        self.websocket.sync_set_message_callback(Callback())
        addrs = self.client.create_elements_by_scs(["concept1 -> node1;;", "concept2 -> node2;;"])
        self.assertEqual(addrs, [True, True])

    def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("string or SCs")):
            # noinspection PyTypeChecker
            self.client.create_elements_by_scs("wrong type here")
            # noinspection PyTypeChecker
            self.client.create_elements_by_scs([1])

    def test_error_params(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                # pylint: disable=unused-argument
                return Response(id_, False, False, [0], [{"message": "Parse error ...", "ref": 0}])

        self.websocket.sync_set_message_callback(Callback())
        with self.assertRaisesRegex(ScServerError, ErrorNotes.GOT_ERROR.format("Parse error ...")):
            self.client.create_elements_by_scs(["concept1 -> ;;"])

    def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        self.websocket.sync_set_message_callback(NoRunCallback())
        result = self.client.create_elements_by_scs([])
        self.assertEqual(result, [])


class GetLinksContentTestCase(ScClientActionsTestCase):
    def test_ok(self):
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

        self.websocket.sync_set_message_callback(Callback())
        contents_received = self.client.get_link_content(ScAddr(1), ScAddr(2), ScAddr(3))
        self.assertEqual(
            contents_received,
            [
                ScLinkContent("str1", content_type=ScLinkContentType.STRING),
                ScLinkContent(1, content_type=ScLinkContentType.INT),
                ScLinkContent(1.0, content_type=ScLinkContentType.FLOAT),
            ],
        )

    def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES_SC_ADDR):
            # noinspection PyTypeChecker
            self.client.get_link_content(12)

    def test_error_params(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                # pylint: disable=unused-argument
                return Response(id_, False, False, None, "Invalid state ...")

        self.websocket.sync_set_message_callback(Callback())
        with self.assertRaisesRegex(ScServerError, ErrorNotes.GOT_ERROR.format("Invalid state ...")):
            self.client.get_link_content(ScAddr(111222))

    def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        self.websocket.sync_set_message_callback(NoRunCallback())
        result = self.client.get_link_content()
        self.assertEqual(result, [])


class SetLinksContentTestCase(ScClientActionsTestCase):
    def test_ok(self):
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

        self.websocket.sync_set_message_callback(Callback())
        addrs = self.client.set_link_contents(
            ScLinkContent("str", ScLinkContentType.STRING, ScAddr(1)),
            ScLinkContent(2, ScLinkContentType.INT, ScAddr(2)),
            ScLinkContent(3.0, ScLinkContentType.FLOAT, ScAddr(3)),
        )
        self.assertTrue(addrs)

    def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScLinkContent")):
            # noinspection PyTypeChecker
            self.client.set_link_contents("wrong type here")

    def test_error_params(self):
        class Callback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                # pylint: disable=unused-argument
                return Response(id_, False, False, [0], [{"message": "Some error on sc-server ....", "ref": 0}])

        self.websocket.sync_set_message_callback(Callback())
        with self.assertRaisesRegex(ScServerError, ErrorNotes.GOT_ERROR.format("Some error on sc-server ....")):
            self.client.set_link_contents(ScLinkContent("str", ScLinkContentType.INT, ScAddr(1)))

    def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        self.websocket.sync_set_message_callback(NoRunCallback())
        result = self.client.set_link_contents()
        self.assertTrue(result)


class GetLinksTestCase(ScClientActionsTestCase):
    params = [
        (ScClient.get_links_by_content, common.CommandTypes.FIND),
        (ScClient.get_links_by_content_substring, common.CommandTypes.FIND_LINKS_BY_SUBSTRING),
        (
            ScClient.get_links_contents_by_content_substring,
            common.CommandTypes.FIND_LINKS_CONTENTS_BY_CONTENT_SUBSTRING,
        ),
    ]

    def test_ok(self):
        for method, command in self.params:
            # pylint: disable=cell-var-from-loop
            class Callback(ResponseCallback):
                def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                    assert type_ == RequestType.CONTENT
                    assert payload_ == [
                        {common.COMMAND: command, common.DATA: data} for data in ("str_content", "str", 12, 3.14)
                    ]
                    return Response(id_, True, False, [[1], [2, 3]], None)

            self.websocket.sync_set_message_callback(Callback())
            contents = [ScLinkContent("str_content", ScLinkContentType.STRING), "str", 12, 3.14]
            method(self.client, *contents)

    def test_wrong_params(self):
        for method, _ in self.params:
            with self.assertRaisesRegex(
                InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScLinkContent, str, int or float")
            ):
                # noinspection PyTypeChecker
                method(self.client, ("wrong type here",))

    def test_error_params(self):
        for method, _ in self.params:

            class Callback(ResponseCallback):
                def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                    # pylint: disable=unused-argument
                    return Response(id_, False, False, [0], [{"message": "Some error on sc-server ....", "ref": 0}])

            self.websocket.sync_set_message_callback(Callback())
            with self.assertRaisesRegex(ScServerError, ErrorNotes.GOT_ERROR.format("Some error on sc-server ....")):
                method(self.client, ScLinkContent("str", ScLinkContentType.INT))

    def test_empty_params(self):
        for method, _ in self.params:

            class NoRunCallback(ResponseCallback):
                def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                    raise AssertionError

            self.websocket.sync_set_message_callback(NoRunCallback())
            result = method(self.client)
            self.assertEqual(result, [])


class ResolveKeynodesTestCase(ScClientActionsTestCase):
    def test_ok(self):
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

        self.websocket.sync_set_message_callback(Callback())
        params = [
            ScIdtfResolveParams("some_class", sc_types.NODE_CONST_CLASS),
            ScIdtfResolveParams("some_node", sc_types.NODE_CONST),
            ScIdtfResolveParams("some_existing_element", None),
        ]
        self.client.resolve_keynodes(*params)

    def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScIdtfResolveParams")):
            self.client.resolve_keynodes(sc_types.NODE_CONST)

    def test_empty_params(self):
        class NoRunCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                raise AssertionError

        self.websocket.sync_set_message_callback(NoRunCallback())
        result = self.client.resolve_keynodes()
        self.assertEqual(result, [])


class TemplateTestCase(ScClientActionsTestCase):
    def test_ok_search_sc_template(self):
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

        self.websocket.sync_set_message_callback(Callback())
        template = ScTemplate().triple(ScAddr(1), sc_types.EDGE_ACCESS_VAR_POS_PERM >> "edge", sc_types.NODE_VAR)
        result = (self.client.template_search(template))[0]
        self.assertEqual(result.addrs, [ScAddr(1), ScAddr(2), ScAddr(3)])
        self.assertEqual(result.aliases, {"edge": 2})

    def test_ok_generate_sc_template(self):
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

        self.websocket.sync_set_message_callback(Callback())
        template = ScTemplate().triple(ScAddr(1), sc_types.EDGE_ACCESS_VAR_POS_PERM >> "edge", ScAddr(3))
        result = self.client.template_generate(template)
        self.assertEqual(result.addrs, [ScAddr(1), ScAddr(2), ScAddr(3)])
        self.assertEqual(result.aliases, {"edge": 2})

    def test_ok_search_scs_template(self):
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

        self.websocket.sync_set_message_callback(Callback())
        template = "person _-> .._p (* _=> nrel_email:: _[test@email.com] *);;"
        params = {".._p": ScAddr(5314)}
        results = self.client.template_search(template, params)
        self.assertEqual(results, [])

    # noinspection PyTypeChecker
    def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScTemplate")):
            self.client.template_search(None)
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScTemplate")):
            self.client.template_generate(None)

    def test_wrong_template(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.VAR_TYPE_IN_TEMPLATE):
            ScTemplate().triple(ScAddr(0), sc_types.EDGE_ACCESS_CONST_POS_PERM, ScAddr(0))


class ScEventsTestCase(ScClientActionsTestCase):
    def test_ok_create_and_destroy(self):
        def test_callback(*_):
            pass

        param = ScEventParams(ScAddr(12), ScEventType.ADD_OUTGOING_EDGE, test_callback)

        class CreateCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == common.RequestType.EVENTS
                nonlocal param
                assert payload_ == {
                    common.CommandTypes.CREATE: [{common.TYPE: param.event_type.value, common.ADDR: param.addr.value}]
                }
                return Response(id_, True, False, [1], None)

        self.websocket.sync_set_message_callback(CreateCallback())
        events = self.client.events_create(param)
        self.assertTrue(self.client.is_event_valid(events[0]))

        class DestroyCallback(ResponseCallback):
            def callback(self, id_: int, type_: common.RequestType, payload_: Any) -> Response:
                assert type_ == common.RequestType.EVENTS
                nonlocal events
                assert payload_ == {common.CommandTypes.DELETE: [event.id for event in events]}
                return Response(id_, True, False, None, None)

        self.websocket.sync_set_message_callback(DestroyCallback())
        is_event_deleted = self.client.events_destroy(*events)
        self.assertTrue(is_event_deleted)
        self.assertFalse(self.client.is_event_valid(events[0]))

    def test_ok_create_and_run_event(self):
        def callback(src: ScAddr, *_):
            nonlocal is_call_succesfull
            is_call_succesfull = src == ScAddr(12)

        is_call_succesfull = False
        self.websocket.sync_set_message_callback(SimpleResponseCallback(True, False, [1], None))
        events = self.client.events_create(ScEventParams(ScAddr(12), ScEventType.ADD_OUTGOING_EDGE, callback))
        self.websocket.messages.put_nowait(
            f'{{"id": {events[0].id}, "event": true, "status": true, "payload": [12, 0, 0], "errors": []}}'
        )
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.01))
        assert is_call_succesfull

    def test_wrong_params(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScEventParams")):
            self.client.events_create("wrong type here")

    def test_is_event_valid_incorrect_arguments(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScEvent")):
            self.client.is_event_valid("wrong type here")

    def test_events_destroy_incorrect_arguments(self):
        with self.assertRaisesRegex(InvalidTypeError, ErrorNotes.EXPECTED_OBJECT_TYPES.format("ScEvent")):
            self.client.events_destroy("wrong type here")
