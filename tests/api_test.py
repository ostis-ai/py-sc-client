"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

import time
import unittest
from unittest.mock import Mock, patch

import pytest

from sc_client import client, session
from sc_client.constants import common, sc_types
from sc_client.constants.exceptions import (
    CommonErrorMessages,
    InvalidTypeError,
    LinkContentOversizeError,
    PayloadMaxSizeError,
    ServerError,
)
from sc_client.constants.numeric import LINK_CONTENT_MAX_SIZE, MAX_PAYLOAD_SIZE
from sc_client.models import (
    ScAddr,
    ScConstruction,
    ScEventSubscription,
    ScEventCallbackFunc,
    ScEventSubscriptionParams,
    ScIdtfResolveParams,
    ScLinkContent,
    ScLinkContentType,
    SCs,
    ScTemplate,
)
from sc_client.sc_keynodes import ScKeynodes

# pylint: disable=W0212


class ScTest(unittest.TestCase):
    def setUp(self) -> None:
        self._mock_ws_app_patcher = patch("sc_client.session._ScClientSession.ws_app")
        self.mock_ws_app = self._mock_ws_app_patcher.start()
        self.mock_ws_app.send = Mock()
        self.mock_ws_app.return_value = Mock()
        session._ScClientSession.is_open = True

    def tearDown(self) -> None:
        self._mock_ws_app_patcher.stop()
        session._ScClientSession.clear()

    @staticmethod
    def get_server_message(response: str):
        session._on_message(session._ScClientSession.ws_app, response)


class TestResponseWithFailedStatus(ScTest):
    def test_incorrect_type(self):
        errors = '"errors": [{"message": "type must be X, but is Y", "ref": 0}]'
        self.get_server_message('{"id": 1, "event": false, "status": 0, "payload": [0], ' + errors + "}")
        with pytest.raises(ServerError):
            client.generate_elements_by_scs(["asd ->"])


class TestWebsocketMaxSize(ScTest):
    def test_more(self):
        link_content = ScLinkContent("0" * LINK_CONTENT_MAX_SIZE, ScLinkContentType.STRING, ScAddr(0))
        link_contents = [link_content] * (1 + MAX_PAYLOAD_SIZE // LINK_CONTENT_MAX_SIZE)
        with pytest.raises(PayloadMaxSizeError):
            client.set_link_contents(*link_contents)


class TestClientGenerateElements(ScTest):
    def test_generate_construction_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.generate_elements("wrong type here")

    def test_generate_empty_construction(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": []}')
        const = ScConstruction()
        addr = client.generate_elements(const)
        assert addr == []

    def test_generate_node(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [59154]}')
        const = ScConstruction()
        const.generate_node(sc_types.NODE_CONST)
        addr = client.generate_elements(const)
        assert len(addr) == 1

    def test_generate_link(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [1182470]}')
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING)
        const = ScConstruction()
        const.generate_link(sc_types.LINK_CONST, link_content)
        addr = client.generate_elements(const)
        assert len(addr) == 1

    def test_generate_link_type_value(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [123211]}')
        link_content = ScLinkContent("World!", ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.generate_link(sc_types.LINK_CONST, link_content)
        addr_list = client.generate_elements(const)
        assert len(addr_list) == 1

    def test_generate_construction_with_connector(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [33, 34, 2224]}')
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING)
        const = ScConstruction()
        const.generate_node(sc_types.NODE_CONST, "node")
        const.generate_link(sc_types.LINK_CONST, link_content, "link")
        const.generate_connector(sc_types.EDGE_ACCESS_CONST_POS_PERM, "node", "link")
        addr_list = client.generate_elements(const)
        assert len(addr_list) == 3

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_create_construction_with_connector(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [33, 34, 2224]}')
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING)
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST, "node")
        const.create_link(sc_types.LINK_CONST, link_content, "link")
        const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, "node", "link")
        addr_list = client.create_elements(const)
        assert len(addr_list) == 3

class TestClientGenerateElementsBySCs(ScTest):
    def test_generate_elements_by_scs_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.generate_elements_by_scs("wrong type here")
        with pytest.raises(InvalidTypeError):
            client.generate_elements_by_scs([1])

    def test_generate_empty_scs_list(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": []}')
        results = client.generate_elements_by_scs([])
        assert results == []

    def test_generate_by_scs(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [1]}')
        results = client.generate_elements_by_scs(["concept1 -> node1;;"])
        assert len(results) == 1
        assert results[0] is True

    def test_generate_by_wrong_scs(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [0]}')
        results = client.generate_elements_by_scs(["concept1 -> ;;"])
        assert len(results) == 1
        assert results[0] is False

    def test_generate_by_scs_with_output_struct(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [1]}')
        results = client.generate_elements_by_scs([SCs("concept1 -> node1;;", ScAddr(1))])
        assert len(results) == 1
        assert results[0] is True

    def test_generate_by_wrong_scs_with_output_struct(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [0]}')
        results = client.generate_elements_by_scs([SCs("concept1 -> ", ScAddr(0))])
        assert len(results) == 1
        assert results[0] is False

    def test_generate_by_scs_with_output_struct_default_scs(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [1]}')
        results = client.generate_elements_by_scs([SCs("concept1 -> node1;;")])
        assert len(results) == 1
        assert results[0] is True

    def test_generate_by_scs_with_output_struct_multiple_scs(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [1, 1]}')
        results = client.generate_elements_by_scs([SCs("concept1 -> node1;;", ScAddr(1)), SCs("concept1 -> node2;;")])
        assert len(results) == 2
        assert results[0] is True and results[1] is True

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_create_by_scs_with_output_struct_multiple_scs(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [1, 1]}')
        results = client.create_elements_by_scs([SCs("concept1 -> node1;;", ScAddr(1)), SCs("concept1 -> node2;;")])
        assert len(results) == 2
        assert results[0] is True and results[1] is True


class TestClientGetElementTypes(ScTest):
    def test_get_elements_types_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.get_elements_types("wrong type here")

    def test_get_node_type(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [33]}')
        node_addr = ScAddr(0)
        elem_types = client.get_elements_types(node_addr)
        assert len(elem_types) == 1
        assert elem_types[0].is_node()

    def test_get_link_type(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [34]}')
        link_addr = ScAddr(0)
        elem_type = client.get_elements_types(link_addr)
        assert len(elem_type), 1
        assert elem_type[0].is_link()

    def test_get_elements_types_list(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [33, 34, 2224]}')
        elem_type_list = client.get_elements_types(ScAddr(0), ScAddr(0), ScAddr(0))
        assert len(elem_type_list) == 3
        assert elem_type_list[0].is_node()
        assert elem_type_list[1].is_link()
        assert elem_type_list[2].is_edge()

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_check_elements_list(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [33, 34, 2224]}')
        elem_type_list = client.check_elements(ScAddr(0), ScAddr(0), ScAddr(0))
        assert len(elem_type_list) == 3
        assert elem_type_list[0].is_node()
        assert elem_type_list[1].is_link()
        assert elem_type_list[2].is_edge()



class TestClientEraseElements(ScTest):
    def test_erase_elements_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.erase_elements("wrong type here")

    def test_erase_empty(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": true}')
        status = client.erase_elements()
        assert status

    def test_erase_node(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": true}')
        node_addr = ScAddr(0)
        status = client.erase_elements(node_addr)
        assert status

    def test_erase_elements_list(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": true}')
        status = client.erase_elements(ScAddr(0), ScAddr(0), ScAddr(0))
        assert status

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_delete_elements_list(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": true}')
        status = client.delete_elements(ScAddr(0), ScAddr(0), ScAddr(0))
        assert status


class TestClientHandleLinkContents(ScTest):
    def test_set_link_contents_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.set_link_contents("wrong type here")

    def test_get_link_content_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.get_link_content("wrong type here")

    def test_search_links_by_contents_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.search_links_by_contents(["wrong type here"])

    def test_set_link_content(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [true]}')
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING)
        link_content.addr = ScAddr(0)
        status = client.set_link_contents(link_content)
        assert status

    def test_set_link_max_content(self):
        test_content = "a" * LINK_CONTENT_MAX_SIZE * 2
        with pytest.raises(LinkContentOversizeError, match=CommonErrorMessages.LINK_OVERSIZE.value):
            ScLinkContent(test_content, ScLinkContentType.STRING)

    def test_get_link_content(self):
        msg = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [{"value": "Hi!", "type": "string"}]}'
        self.get_server_message(msg)
        link_addr = ScAddr(0)
        content = client.get_link_content(link_addr)[0]
        assert content.content_type
        assert content.data
        assert content.addr is None

    def test_search_link_by_content_empty(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [[]]}')
        test_str = "that line nor in KB"
        link_content = ScLinkContent(test_str, ScLinkContentType.STRING)
        content = client.search_links_by_contents(link_content)
        assert content == [[]]

    def test_search_link_by_content_casual(self):
        msg = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [[1179679, 46368, 1181734]]}'
        self.get_server_message(msg)
        test_str = "testing search by link content"
        link_content = ScLinkContent(test_str, ScLinkContentType.STRING)
        content = client.search_links_by_contents(link_content)
        assert content
        link_addr = ScAddr(46368)
        for item in zip([link_addr], content):
            assert item[0].value in [addr.value for addr in item[1]]

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_get_link_by_content_casual(self):
        msg = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [[1179679, 46368, 1181734]]}'
        self.get_server_message(msg)
        test_str = "testing search by link content"
        link_content = ScLinkContent(test_str, ScLinkContentType.STRING)
        content = client.get_links_by_content(link_content)
        assert content
        link_addr = ScAddr(46368)
        for item in zip([link_addr], content):
            assert item[0].value in [addr.value for addr in item[1]]

    def test_search_link_by_content_str(self):
        msg = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [[1179649, 1180550, 1181798]]}'
        self.get_server_message(msg)
        test_str = "testing search by link content as string"
        content = client.search_links_by_contents(test_str)
        assert content
        link_addr = ScAddr(1180550)
        for item in zip([link_addr], content):
            assert item[0].value in [addr.value for addr in item[1]]

    def test_search_link_by_content_multiple(self):
        payload = "[[65504, 1179679, 46368], [46400, 1179711, 46336]]"
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": ' + payload + "}")
        test_str_1 = "testing search by link content as string in multiple content"
        test_str_2 = "testing search by link content as casual in multiple content"
        link_content_2 = ScLinkContent(test_str_2, ScLinkContentType.STRING)
        content = client.search_links_by_contents(test_str_1, link_content_2)
        addr_list = [ScAddr(46368), ScAddr(46400)]
        assert content
        for item in zip(addr_list, content):
            assert item[0].value in [addr.value for addr in item[1]]

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_search_link_by_content_substring(self):
        msg = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [[1179649, 1180550, 1181798]]}'
        self.get_server_message(msg)
        test_str = "testing search by"
        content = client.get_links_by_content_substring(test_str)
        assert content
        link_addr = ScAddr(1180550)
        for item in zip([link_addr], content):
            assert item[0].value in [addr.value for addr in item[1]]

    def test_get_link_by_content_substring(self):
        msg = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [[1179649, 1180550, 1181798]]}'
        self.get_server_message(msg)
        test_str = "testing search by"
        content = client.search_links_by_contents_substrings(test_str)
        assert content
        link_addr = ScAddr(1180550)
        for item in zip([link_addr], content):
            assert item[0].value in [addr.value for addr in item[1]]

    def test_search_link_contents_by_content_substrings(self):
        msg = (
            '{"errors": [], "id": 1, "event": false, "status": true, "payload": [["concept_test", "class_concept", '
            '"content"]]} '
        )
        self.get_server_message(msg)
        test_str = "con"
        content = client.search_link_contents_by_content_substrings(test_str)
        assert content
        strings = ["concept_test", "class_concept", "content"]
        for item in zip(strings, content):
            assert item[0] in item[1]

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_get_links_contents_by_content_substring(self):
        msg = (
            '{"errors": [], "id": 1, "event": false, "status": true, "payload": [["concept_test", "class_concept", '
            '"content"]]} '
        )
        self.get_server_message(msg)
        test_str = "con"
        content = client.get_links_contents_by_content_substring(test_str)
        assert content
        strings = ["concept_test", "class_concept", "content"]
        for item in zip(strings, content):
            assert item[0] in item[1]



class TestClientResolveElements(ScTest):
    def test_resolve_keynodes_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.resolve_keynodes("wrong type here")

    def test_resolve_keynode_not_exist(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [1183238]}')
        params = ScIdtfResolveParams(idtf="my_new_keynode_that_not_exist", type=sc_types.NODE_CONST)
        addr = client.resolve_keynodes(params)
        assert addr[0].value != 0

    def test_resolve_keynode_exist(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [337259]}')
        params = ScIdtfResolveParams(idtf="technology_OSTIS", type=sc_types.NODE_CONST)
        addr = client.resolve_keynodes(params)
        assert addr[0].value != 0

    def test_find_keynode_not_exist(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [0]}')
        params = ScIdtfResolveParams(idtf="my_another_keynode_that_not_exist", type=None)
        addr = client.resolve_keynodes(params)
        assert addr[0].is_valid() is False

    def test_find_keynode_exist(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [900]}')
        params = ScIdtfResolveParams(idtf="nrel_format", type=None)
        addr = client.resolve_keynodes(params)
        assert addr[0].value != 0

    def test_find_keynode_exist_no_type(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [900]}')
        params = ScIdtfResolveParams(idtf="nrel_format", type=None)
        addr = client.resolve_keynodes(params)
        assert addr[0].value != 0

    def test_resolve_keynodes_list(self):
        msg = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [1183238, 337259, 0]}'
        self.get_server_message(msg)
        param1 = ScIdtfResolveParams(idtf="my_new_keynode_that_not_exist", type=sc_types.NODE_CONST)
        param2 = ScIdtfResolveParams(idtf="technology_OSTIS", type=sc_types.NODE_CONST)
        param3 = ScIdtfResolveParams(idtf="my_another_keynode_that_not_exist", type=None)
        addrs = client.resolve_keynodes(param1, param2, param3)
        assert len(addrs) == 3
        assert addrs[0].value != 0
        assert addrs[1].value != 0
        assert addrs[2].value == 0


class TestClientResolveKeynodes(ScTest):
    def test_resolve_keynode_not_exist_node(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [1183238]}')
        keynodes = ScKeynodes()
        mega_new_keynode = keynodes['mega_new_keynode', sc_types.NODE_CONST]
        assert mega_new_keynode.value != 0

    def test_resolve_keynode_not_exist_link(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [1183238]}')
        keynodes = ScKeynodes()
        mega_new_keynode = keynodes['mega_new_keynode', sc_types.LINK_CONST]
        assert mega_new_keynode.value != 0

    def test_resolve_keynode_not_exist_without_type(self):
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": [1183238]}')
        keynodes = ScKeynodes()
        mega_new_keynode = keynodes['mega_new_keynode']
        assert mega_new_keynode.value != 0


class TestClientHandleEventSubscriptions(ScTest):
    def test_create_elementary_event_subscriptions_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.create_elementary_event_subscriptions("wrong type here")

    def test_is_event_valid_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.is_event_subscription_valid("wrong type here")

    def test_events_destroy_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.destroy_elementary_event_subscriptions("wrong type here")

    def _create_event_subscription(self, server_message: str, addr_value: int, callback: ScEventCallbackFunc) -> ScEventSubscription:
        self.get_server_message(server_message)
        event_params = ScEventSubscriptionParams(ScAddr(addr_value), common.ScEventType.BEFORE_ERASE_ELEMENT, callback)
        event_subscription = client.create_elementary_event_subscriptions(event_params)
        assert client.is_event_subscription_valid(event_subscription[0])
        return event_subscription[0]

    def test_create_and_emit_events(self):
        def test_callback(*_):
            nonlocal is_called
            is_called = True

        is_called = False
        server_message = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [19]}'
        addr_value = 1183238
        self._create_event_subscription(server_message, addr_value, test_callback)
        time.sleep(0.1)
        self.get_server_message('{"errors": [], "id": 19, "event": true, "status": true, "payload": [1183238, 0, 0]}')
        assert is_called

    def test_multiple_events(self):
        def test_callback_1(*_):
            res_msg = '{"errors": [], "id": 3, "event": true, "status": true, "payload": [1183974, 1184230, 1184102]}'
            self.get_server_message(res_msg)

        def test_callback_2(*_):
            nonlocal is_called
            is_called = True

        is_called = False
        server_message_1 = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [2]}'
        server_message_2 = '{"errors": [], "id": 2, "event": false, "status": true, "payload": [3]}'
        addr_value_1 = 1183238
        addr_value_2 = 1183974
        self._create_event_subscription(server_message_1, addr_value_1, test_callback_1)
        self._create_event_subscription(server_message_2, addr_value_2, test_callback_2)

        msg = '{"errors": [], "id": 2, "event": true, "status": true, "payload": [1183334, 45600, 1183974]}'
        self.get_server_message(msg)
        time.sleep(0.1)
        assert is_called

    def test_destroy_elementary_event_subscriptions(self):
        def test_callback(*_):
            nonlocal is_called
            is_called = True

        is_called = False
        server_message = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [19]}'
        addr_value = 1183238
        event_subscription = self._create_event_subscription(server_message, addr_value, test_callback)

        self.get_server_message('{"errors": [], "id": 2, "event": false, "status": true, "payload": []}')
        client.destroy_elementary_event_subscriptions(event_subscription)
        assert client.is_event_subscription_valid(event_subscription) is False

        time.sleep(0.1)
        self.get_server_message('{"errors": [], "id": 19, "event": true, "status": true, "payload": [1183238, 0, 0]}')
        assert is_called is False


class TestClientHandleDeprecatedEventSubscriptions(ScTest):
    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_create_elementary_event_subscriptions_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.events_create("wrong type here")

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_is_event_valid_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.is_event_valid("wrong type here")

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_events_destroy_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.events_destroy("wrong type here")

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def _create_event_subscription(self, server_message: str, addr_value: int, callback: ScEventCallbackFunc) -> ScEventSubscription:
        self.get_server_message(server_message)
        event_params = ScEventSubscriptionParams(ScAddr(addr_value), common.ScEventType.BEFORE_ERASE_ELEMENT, callback)
        event_subscription = client.events_create(event_params)
        assert client.is_event_valid(event_subscription[0])
        return event_subscription[0]

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_create_and_emit_events(self):
        def test_callback(*_):
            nonlocal is_called
            is_called = True

        is_called = False
        server_message = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [19]}'
        addr_value = 1183238
        self._create_event_subscription(server_message, addr_value, test_callback)
        time.sleep(0.1)
        self.get_server_message('{"errors": [], "id": 19, "event": true, "status": true, "payload": [1183238, 0, 0]}')
        assert is_called

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_multiple_events(self):
        def test_callback_1(*_):
            res_msg = '{"errors": [], "id": 3, "event": true, "status": true, "payload": [1183974, 1184230, 1184102]}'
            self.get_server_message(res_msg)

        def test_callback_2(*_):
            nonlocal is_called
            is_called = True

        is_called = False
        server_message_1 = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [2]}'
        server_message_2 = '{"errors": [], "id": 2, "event": false, "status": true, "payload": [3]}'
        addr_value_1 = 1183238
        addr_value_2 = 1183974
        self._create_event_subscription(server_message_1, addr_value_1, test_callback_1)
        self._create_event_subscription(server_message_2, addr_value_2, test_callback_2)

        msg = '{"errors": [], "id": 2, "event": true, "status": true, "payload": [1183334, 45600, 1183974]}'
        self.get_server_message(msg)
        time.sleep(0.1)
        assert is_called

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_destroy_elementary_event_subscriptions(self):
        def test_callback(*_):
            nonlocal is_called
            is_called = True

        is_called = False
        server_message = '{"errors": [], "id": 1, "event": false, "status": true, "payload": [19]}'
        addr_value = 1183238
        event_subscription = self._create_event_subscription(server_message, addr_value, test_callback)

        self.get_server_message('{"errors": [], "id": 2, "event": false, "status": true, "payload": []}')
        client.events_destroy(event_subscription)
        assert client.is_event_valid(event_subscription) is False

        time.sleep(0.1)
        self.get_server_message('{"errors": [], "id": 19, "event": true, "status": true, "payload": [1183238, 0, 0]}')
        assert is_called is False


class TestClientHandleTemplates(ScTest):
    def test_search_by_template_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.search_by_template(["wrong type here"])
        with pytest.raises(InvalidTypeError):
            client.search_by_template("wrong type", "here")

    def test_generate_by_template_incorrect_arguments(self):
        with pytest.raises(InvalidTypeError):
            client.generate_by_template(["wrong type here"])
        with pytest.raises(InvalidTypeError):
            client.generate_by_template("wrong type", "here")

    def test_wrong_template(self):
        with pytest.raises(InvalidTypeError):
            templ = ScTemplate()
            templ.triple(ScAddr(0), sc_types.EDGE_ACCESS_CONST_POS_PERM, ScAddr(0))

        with pytest.raises(InvalidTypeError):
            templ = ScTemplate()
            templ.triple((ScAddr(0), "_class_node"), ScAddr(0), (sc_types.LINK_CONST, "_const_link"))

        with pytest.raises(InvalidTypeError):
            templ = ScTemplate()
            templ.quintuple(
                ScAddr(0) >> "_main_node",
                sc_types.EDGE_D_COMMON_CONST >> "_const_edge",
                sc_types.LINK_VAR >> "_link",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                ScAddr(0),
            )
        
    def test_search_by_template(self):
        payload = (
            '{"aliases": {"_class_node": 0}, "addrs": '
            "[[1184838, 1184902, 1184870, 1184838, 1184934, 1184774, 1184838, 1184966, 1184806, 0, 0, 0]]}"
        )
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": ' + payload + "}")
        templ = ScTemplate()
        templ.triple((ScAddr(0), "_class_node"), sc_types.EDGE_ACCESS_VAR_POS_PERM, ScAddr(0))
        templ.triple("_class_node", sc_types.EDGE_ACCESS_VAR_POS_TEMP, ScAddr(0))
        templ.triple("_class_node", ScAddr(0), sc_types.NODE_VAR)
        templ.triple(ScAddr(0), ScAddr(0), sc_types.NODE_VAR)
        search_result_list = client.search_by_template(templ, {})

        assert len(search_result_list) != 0
        search_result = search_result_list[0]
        assert len(search_result) == 12
        assert search_result.get("_class_node").value == search_result.get(0).value
        for item in search_result:
            for element in item:
                assert isinstance(element, ScAddr)

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_template_search(self):
        payload = (
            '{"aliases": {"_class_node": 0}, "addrs": '
            "[[1184838, 1184902, 1184870, 1184838, 1184934, 1184774, 1184838, 1184966, 1184806, 0, 0, 0]]}"
        )
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": ' + payload + "}")
        templ = ScTemplate()
        templ.triple((ScAddr(0), "_class_node"), sc_types.EDGE_ACCESS_VAR_POS_PERM, ScAddr(0))
        templ.triple("_class_node", sc_types.EDGE_ACCESS_VAR_POS_TEMP, ScAddr(0))
        templ.triple("_class_node", ScAddr(0), sc_types.NODE_VAR)
        templ.triple(ScAddr(0), ScAddr(0), sc_types.NODE_VAR)
        search_result_list = client.template_search(templ, {})

        assert len(search_result_list) != 0
        search_result = search_result_list[0]
        assert len(search_result) == 12
        assert search_result.get("_class_node").value == search_result.get(0).value
        for item in search_result:
            for element in item:
                assert isinstance(element, ScAddr)

    def test_search_by_template_by_idtf(self):
        payload = '{"aliases": {"_class_node": 0}, "addrs": [[1184838, 1184902, 1184870, 1184838, 1184934, 1184774]]}'
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": ' + payload + "}")
        params = {"_class_node": "my_class"}
        search_result_list = client.search_by_template("my_template", params)

        assert len(search_result_list) != 0
        search_result = search_result_list[0]
        assert len(search_result) == 6
        assert search_result.get("_class_node").value == search_result[0].value
        for src, connector, trg in search_result:
            for addr in (src, connector, trg):
                assert isinstance(addr, ScAddr)

    def test_search_by_template_by_addr(self):
        payload = '{"aliases": {}, "addrs": [[1184838, 1184902, 1184870, 1184838, 1184934, 1184774]]}'
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": ' + payload + "}")
        search_result_list = client.search_by_template(ScAddr(154454))

        assert len(search_result_list) != 0
        search_result = search_result_list[0]
        assert len(search_result) == 6
        for src, connector, trg in search_result:
            for addr in (src, connector, trg):
                assert isinstance(addr, ScAddr)

    def test_generate_by_template(self):
        payload = (
            '{"aliases": {"_link": 2, "_main_node": 0, "_var_node": 8, "edge_1_0": 1}, '
            '"addrs": [1245352, 1245449, 1245384, 1245320, 1245481, 1245449, 1245352, 1245513, 1245288]}'
        )
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": ' + payload + "}")

        templ = ScTemplate()
        templ.quintuple(
            (ScAddr(0), "_main_node"),
            sc_types.EDGE_D_COMMON_VAR,
            (sc_types.LINK_VAR, "_link"),
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScAddr(0),
        )
        templ.triple("_main_node", sc_types.EDGE_ACCESS_VAR_POS_TEMP, (sc_types.NODE_VAR, "_var_node"))

        gen_params = {"_link": ScAddr(0), "_var_node": ScAddr(0)}
        gen_result = client.generate_by_template(templ, gen_params)
        assert len(gen_result) == 9

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_template_generate(self):
        payload = (
            '{"aliases": {"_link": 2, "_main_node": 0, "_var_node": 8, "edge_1_0": 1}, '
            '"addrs": [1245352, 1245449, 1245384, 1245320, 1245481, 1245449, 1245352, 1245513, 1245288]}'
        )
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": ' + payload + "}")

        templ = ScTemplate()
        templ.quintuple(
            (ScAddr(0), "_main_node"),
            sc_types.EDGE_D_COMMON_VAR,
            (sc_types.LINK_VAR, "_link"),
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScAddr(0),
        )
        templ.triple("_main_node", sc_types.EDGE_ACCESS_VAR_POS_TEMP, (sc_types.NODE_VAR, "_var_node"))

        gen_params = {"_link": ScAddr(0), "_var_node": ScAddr(0)}
        gen_result = client.template_generate(templ, gen_params)
        assert len(gen_result) == 9

    def test_generate_by_template_by_idtf(self):
        payload = '{"aliases": {}, "addrs": [1245352, 1245449, 1245384, 1245352, 1245513, 1245288]}'
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": ' + payload + "}")

        gen_result = client.generate_by_template("my_template")
        assert len(gen_result) == 6

    def test_generate_by_template_by_addr(self):
        payload = (
            '{"aliases": {"_link": 2, "_main_node": 0, "_var_node": 8, "edge_1_0": 1}, '
            '"addrs": [1245352, 1245449, 1245384, 1245320, 1245481, 1245449, 1245352, 1245513, 1245288]}'
        )
        self.get_server_message('{"errors": [], "id": 1, "event": false, "status": true, "payload": ' + payload + "}")

        gen_params = {"_link": ScAddr(0), "_var_node": ScAddr(0)}
        gen_result = client.generate_by_template(ScAddr(0), gen_params)
        assert len(gen_result) == 9


client_test_cases = (
    TestClientGenerateElements,
    TestClientGetElementTypes,
    TestClientEraseElements,
    TestClientResolveElements,
    TestClientResolveKeynodes,
    TestClientHandleLinkContents,
    TestClientHandleTemplates,
    TestClientHandleEventSubscriptions,
)
