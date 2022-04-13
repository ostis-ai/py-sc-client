"""
    Copyright (c) 2022 Intelligent Semantic Systems LLC, All rights reserved.
    Author Nikiforov Sergei
    Author Alexandr Zagorskiy
"""

import time
import unittest
from unittest.mock import Mock, patch

from sc_client import client
from sc_client.constants import common, sc_types
from sc_client.constants.exceptions import LinkContentOversizeError
from sc_client.constants.numeric import LINK_CONTENT_MAX_SIZE
from sc_client.dataclass import (
    ScAddr,
    ScConstruction,
    ScEventParams,
    ScIdtfResolveParams,
    ScLinkContent,
    ScLinkContentType,
    ScTemplate, ScEventCallbackFunc, ScEvent,
)


class ScTest(unittest.TestCase):
    def setUp(self) -> None:
        self._mock_ws_app_patcher = patch('sc_client.client._ScClient.ws_app')
        self.mock_ws_app = self._mock_ws_app_patcher.start()
        self.mock_ws_app.return_value = Mock()

    def tearDown(self) -> None:
        self._mock_ws_app_patcher.stop()
        client._ScClient.clear()

    @staticmethod
    def get_server_message(response: str):
        client._on_message(client._ScClient.ws_app, response)


class ClientTestCreateElements(ScTest):
    def test_create_empty_construction(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": []}')
        const = ScConstruction()
        addr = client.create_elements(const)
        self.assertFalse(addr)

    def test_create_node(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [59154]}')
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST)
        addr = client.create_elements(const)
        self.assertEqual(len(addr), 1)

    def test_create_link(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [1182470]}')
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_link(sc_types.LINK, link_content)
        addr = client.create_elements(const)
        self.assertEqual(len(addr), 1)

    def test_create_construction_with_edge(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [33, 34, 2224]}')
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST, "node")
        const.create_link(sc_types.LINK, link_content, "link")
        const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, "node", "link")
        addr_list = client.create_elements(const)
        self.assertEqual(len(addr_list), 3)


class ClientTestCheckElements(ScTest):
    def test_check_node(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [33]}')
        node_addr = ScAddr(0)
        elem_types = client.check_elements([node_addr])
        self.assertEqual(len(elem_types), 1)
        self.assertTrue(elem_types[0].is_node())

    def test_check_link(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [34]}')
        link_addr = ScAddr(0)
        elem_type = client.check_elements([link_addr])
        self.assertEqual(len(elem_type), 1)
        self.assertTrue(elem_type[0].is_link())

    def test_check_elements_list(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [33, 34, 2224]}')
        addr_list = [ScAddr(0), ScAddr(0), ScAddr(0)]
        elem_type_list = client.check_elements(addr_list)
        self.assertEqual(len(elem_type_list), 3)
        self.assertTrue(elem_type_list[0].is_node())
        self.assertTrue(elem_type_list[1].is_link())
        self.assertTrue(elem_type_list[2].is_edge())


class ClientTestDeleteElements(ScTest):
    def test_delete_empty(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": true}')
        status = client.delete_elements([])
        self.assertTrue(status)

    def test_delete_node(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": true}')
        node_addr = ScAddr(0)
        status = client.delete_elements([node_addr])
        self.assertTrue(status)

    def test_delete_elements_list(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": true}')
        addr_list = [ScAddr(0), ScAddr(0), ScAddr(0)]
        status = client.delete_elements(addr_list)
        self.assertTrue(status)


class ClientTestLinkContent(ScTest):
    def test_set_link_content(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [true]}')
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
        link_content.addr = ScAddr(0)
        status = client.set_link_contents([link_content])
        self.assertTrue(status)

    def test_set_link_max_content(self):
        test_content = "a" * LINK_CONTENT_MAX_SIZE * 2
        with self.assertRaises(LinkContentOversizeError):
            ScLinkContent(test_content, ScLinkContentType.STRING.value)

    def test_get_link_content(self):
        msg = '{"id": 1, "event": false, "status": true, "payload": [{"value": "Hi!", "type": "string"}]}'
        self.get_server_message(msg)
        link_addr = ScAddr(0)
        content = client.get_link_content(link_addr)
        self.assertTrue(content.addr)

    def test_get_link_by_content_empty(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [[]]}')
        test_str = "that line nor in KB"
        link_content = ScLinkContent(test_str, ScLinkContentType.STRING.value)
        content = client.get_link_by_content([link_content])
        self.assertTrue(content)
        self.assertFalse(content[0])

    def test_get_link_by_content_casual(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [[1179679, 46368, 1181734]]}')
        test_str = "testing search by link content"
        link_content = ScLinkContent(test_str, ScLinkContentType.STRING.value)
        content = client.get_link_by_content([link_content])
        self.assertTrue(content)
        link_addr = ScAddr(46368)
        for item in zip([link_addr], content):
            self.assertTrue(item[0].value in [addr.value for addr in item[1]])

    def test_get_link_by_content_str(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [[1179649, 1180550, 1181798]]}')
        test_str = "testing search by link content as string"
        content = client.get_link_by_content([test_str])
        self.assertTrue(content)
        link_addr = ScAddr(1180550)
        for item in zip([link_addr], content):
            self.assertTrue(item[0].value in [addr.value for addr in item[1]])

    def test_get_link_by_content_multiple(self):
        payload = '[[65504, 1179679, 46368], [46400, 1179711, 46336]]'
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": ' + payload + '}')
        test_str_1 = "testing search by link content as string in multiple content"
        test_str_2 = "testing search by link content as casual in multiple content"
        link_content_2 = ScLinkContent(test_str_2, ScLinkContentType.STRING.value)
        content = client.get_link_by_content([test_str_1, link_content_2])
        addr_list = [ScAddr(46368), ScAddr(46400)]
        self.assertTrue(content)
        for item in zip(addr_list, content):
            self.assertTrue(item[0].value in [addr.value for addr in item[1]])


class ClientTestResolveElements(ScTest):
    def test_resolve_keynode_not_exist(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [1183238]}')
        params = ScIdtfResolveParams(idtf="my_new_keynode_that_not_exist", type=sc_types.NODE_CONST)
        addr = client.resolve_keynodes([params])
        self.assertNotEqual(addr[0].value, 0)

    def test_resolve_keynode_exist(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [337259]}')
        params = ScIdtfResolveParams(idtf="technology_OSTIS", type=sc_types.NODE_CONST)
        addr = client.resolve_keynodes([params])
        self.assertNotEqual(addr[0].value, 0)

    def test_find_keynode_not_exist(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [0]}')
        params = ScIdtfResolveParams(idtf="my_another_keynode_that_not_exist", type=None)
        addr = client.resolve_keynodes([params])
        self.assertEqual(addr[0].value, 0)

    def test_find_keynode_exist(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [900]}')
        params = ScIdtfResolveParams(idtf="nrel_format", type=None)
        addr = client.resolve_keynodes([params])
        self.assertNotEqual(addr[0].value, 0)

    def test_resolve_keynodes_list(self):
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": [1183238, 337259, 0]}')
        param1 = ScIdtfResolveParams(idtf="my_new_keynode_that_not_exist", type=sc_types.NODE_CONST)
        param2 = ScIdtfResolveParams(idtf="technology_OSTIS", type=sc_types.NODE_CONST)
        param3 = ScIdtfResolveParams(idtf="my_another_keynode_that_not_exist", type=None)
        addrs = client.resolve_keynodes([param1, param2, param3])
        self.assertEqual(len(addrs), 3)
        self.assertNotEqual(addrs[0].value, 0)
        self.assertNotEqual(addrs[1].value, 0)
        self.assertEqual(addrs[2].value, 0)


class ClientTestEvent(ScTest):
    def _create_event(self, server_message: str, addr_value: int, callback: ScEventCallbackFunc) -> ScEvent:
        self.get_server_message(server_message)
        event_params = ScEventParams(ScAddr(addr_value), common.ScEventType.REMOVE_ELEMENT, callback)
        sc_event = client.events_create([event_params])
        self.assertTrue(client.is_event_valid(sc_event[0]))
        return sc_event[0]

    def test_create_and_emit_event(self):
        def test_callback(subscribed_el: ScAddr, edge: ScAddr, init_el: ScAddr):
            nonlocal is_called
            is_called = True

        is_called = False
        server_message = '{"id": 1, "event": false, "status": true, "payload": [19]}'
        addr_value = 1183238
        self._create_event(server_message, addr_value, test_callback)
        time.sleep(0.1)
        self.get_server_message('{"id": 19, "event": true, "status": true, "payload": [1183238, 0, 0]}')
        self.assertTrue(is_called)

    def test_multiple_events(self):
        def test_callback_1(src: ScAddr, edge: ScAddr, trg: ScAddr):
            self.get_server_message('{"id": 3, "event": true, "status": true, "payload": [1183974, 1184230, 1184102]}')

        def test_callback_2(src: ScAddr, edge: ScAddr, trg: ScAddr):
            nonlocal is_called
            is_called = True

        is_called = False
        server_message_1 = '{"id": 1, "event": false, "status": true, "payload": [2]}'
        server_message_2 = '{"id": 2, "event": false, "status": true, "payload": [3]}'
        addr_value_1 = 1183238
        addr_value_2 = 1183974
        self._create_event(server_message_1, addr_value_1, test_callback_1)
        self._create_event(server_message_2, addr_value_2, test_callback_2)

        self.get_server_message('{"id": 2, "event": true, "status": true, "payload": [1183334, 45600, 1183974]}')
        time.sleep(0.1)
        self.assertTrue(is_called)

    def test_destroy_event(self):
        def test_callback(subscribed_el: ScAddr, edge: ScAddr, init_el: ScAddr):
            nonlocal is_called
            is_called = True

        is_called = False
        server_message = '{"id": 1, "event": false, "status": true, "payload": [19]}'
        addr_value = 1183238
        sc_event = self._create_event(server_message, addr_value, test_callback)

        self.get_server_message('{"id": 2, "event": false, "status": true, "payload": []}')
        client.events_destroy([sc_event])
        self.assertIsNone(client.is_event_valid(sc_event))

        time.sleep(0.1)
        self.get_server_message('{"id": 19, "event": true, "status": true, "payload": [1183238, 0, 0]}')
        self.assertFalse(is_called)


class ClientTestTemplate(ScTest):
    def test_template_search(self):
        def for_each_tripple_func(src: ScAddr, edge: ScAddr, trg: ScAddr):
            for addr in [src, edge, trg]:
                self.assertTrue(isinstance(addr, ScAddr))

        payload = '{"aliases": {"_class_node": 0}, "addrs": ' \
                  '[[1184838, 1184902, 1184870, 1184838, 1184934, 1184774, 1184838, 1184966, 1184806, 0, 0, 0]]}'
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": ' + payload + '}')
        templ = ScTemplate()
        templ.triple([ScAddr(0), "_class_node"], sc_types.EDGE_ACCESS_VAR_POS_PERM, ScAddr(0))
        templ.triple("_class_node", sc_types.EDGE_ACCESS_VAR_POS_TEMP, ScAddr(0))
        templ.triple("_class_node", ScAddr(0), sc_types.NODE_VAR)
        templ.triple(ScAddr(0), ScAddr(0), sc_types.NODE_VAR, is_required=False)
        search_result_list = client.template_search(templ)

        self.assertNotEqual(len(search_result_list), 0)
        search_result = search_result_list[0]
        self.assertEqual(search_result.size(), 12)
        self.assertEqual(search_result.get("_class_node").value, search_result.get(0).value)
        search_result.for_each_triple(for_each_tripple_func)

    def test_template_generate(self):
        payload = '{"aliases": {"_link": 2, "_main_node": 0, "_var_node": 8, "edge_1_0": 1}, ' \
                  '"addrs": [1245352, 1245449, 1245384, 1245320, 1245481, 1245449, 1245352, 1245513, 1245288]}'
        self.get_server_message('{"id": 1, "event": false, "status": true, "payload": ' + payload + '}')

        templ = ScTemplate()
        templ.triple_with_relation(
            [ScAddr(0), "_main_node"],
            sc_types.EDGE_D_COMMON_VAR,
            [sc_types.LINK, "_link"],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScAddr(0),
        )
        templ.triple("_main_node", sc_types.EDGE_ACCESS_VAR_POS_TEMP, [sc_types.NODE_VAR, "_var_node"])

        gen_params = {"_link": ScAddr(0), "_var_node": ScAddr(0)}
        gen_result = client.template_generate(templ, gen_params)
        self.assertEqual(gen_result.size(), 9)
