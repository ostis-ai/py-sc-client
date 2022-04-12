"""
    Copyright (c) 2022 Intelligent Semantic Systems LLC, All rights reserved.
    Author Nikiforov Sergei
    Author Alexandr Zagorskiy
"""

import time
import unittest

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
    ScTemplate,
)


class ScTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        client.connect("ws://localhost:8090/ws_json")
        if not client.is_connected():
            raise unittest.SkipTest("Platform server is not active")
        cls.setup_class()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.teardown_class()
        client.disconnect()

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass


class ClientTest(ScTest):
    def test_create_empty_construction(self):
        const = ScConstruction()
        addr = client.create_elements(const)
        self.assertFalse(addr)

    def test_create_node(self):
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST)
        addr = client.create_elements(const)
        self.assertEqual(len(addr), 1)

    def test_create_link(self):
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_link(sc_types.LINK, link_content)
        addr = client.create_elements(const)
        self.assertEqual(len(addr), 1)

    def test_create_construction_with_edge(self):
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST, "node")
        const.create_link(sc_types.LINK, link_content, "link")
        const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, "node", "link")
        addr_list = client.create_elements(const)
        self.assertEqual(len(addr_list), 3)

    def test_check_node(self):
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST, "node")
        addr = client.create_elements(const)
        self.assertEqual(len(addr), 1)
        elem_types = client.check_elements(addr)
        self.assertEqual(len(elem_types), 1)
        self.assertTrue(elem_types[0].is_node())

    def test_check_link(self):
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_link(sc_types.LINK, link_content)
        addr = client.create_elements(const)
        self.assertEqual(len(addr), 1)
        elem_type = client.check_elements(addr)
        self.assertEqual(len(elem_type), 1)
        self.assertTrue(elem_type[0].is_link())

    def test_check_elements_list(self):
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST, "node")
        const.create_link(sc_types.LINK, link_content, "link")
        const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, "node", "link")
        addr_list = client.create_elements(const)
        self.assertEqual(len(addr_list), 3)
        elem_type_list = client.check_elements(addr_list)
        self.assertEqual(len(elem_type_list), 3)
        self.assertTrue(elem_type_list[0].is_node())
        self.assertTrue(elem_type_list[1].is_link())
        self.assertTrue(elem_type_list[2].is_edge())

    def test_delete_empty(self):
        status = client.delete_elements([])
        self.assertTrue(status)

    def test_delete_node(self):
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST, "node")
        addr = client.create_elements(const)
        self.assertEqual(len(addr), 1)
        status = client.delete_elements(addr)
        self.assertTrue(status)

    def test_delete_link(self):
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST, "node")
        addr = client.create_elements(const)
        self.assertEqual(len(addr), 1)
        status = client.delete_elements(addr)
        self.assertTrue(status)

    def test_delete_elements_list(self):
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST, "node")
        const.create_link(sc_types.LINK, link_content, "link")
        const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, "node", "link")
        addr_list = client.create_elements(const)
        self.assertEqual(len(addr_list), 3)
        status = client.delete_elements(addr_list)
        self.assertTrue(status)

    def test_set_link_content(self):
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_link(sc_types.LINK, link_content, "link")
        addr_list = client.create_elements(const)
        link_content.addr = addr_list[0]
        link_content.data = "world"
        status = client.set_link_contents([link_content])
        self.assertTrue(status)

    def test_set_link_max_content(self):
        test_content = "a" * LINK_CONTENT_MAX_SIZE * 2
        with self.assertRaises(LinkContentOversizeError):
            ScLinkContent(test_content, ScLinkContentType.STRING.value)

    def test_get_link_content(self):
        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_link(sc_types.LINK, link_content)
        addr_list = client.create_elements(const)
        content = client.get_link_content(addr_list[0])
        self.assertTrue(content.addr)

    def test_get_link_by_content_empty(self):
        test_str = "that line nor in KB"
        link_content = ScLinkContent(test_str, ScLinkContentType.STRING.value)
        content = client.get_link_by_content([link_content])
        self.assertTrue(content)
        self.assertFalse(content[0])

    def test_get_link_by_content_casual(self):
        test_str = "testing search by link content"
        link_content = ScLinkContent(test_str, ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_link(sc_types.LINK, link_content)
        addr_list = client.create_elements(const)
        self.assertTrue(addr_list)
        content = client.get_link_by_content([link_content])
        self.assertTrue(content)
        for item in zip(addr_list, content):
            self.assertTrue(item[0].value in [addr.value for addr in item[1]])

    def test_get_link_by_content_str(self):
        test_str = "testing search by link content as string"
        link_content = ScLinkContent(test_str, ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_link(sc_types.LINK, link_content)
        addr_list = client.create_elements(const)
        self.assertTrue(addr_list)
        content = client.get_link_by_content([test_str])
        self.assertTrue(content)
        for item in zip(addr_list, content):
            self.assertTrue(item[0].value in [addr.value for addr in item[1]])

    def test_get_link_by_content_multiple(self):
        test_str_1 = "testing search by link content as string in multiple content"
        test_str_2 = "testing search by link content as casual in multiple content"
        link_content_1 = ScLinkContent(test_str_1, ScLinkContentType.STRING.value)
        link_content_2 = ScLinkContent(test_str_2, ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_link(sc_types.LINK, link_content_1)
        const.create_link(sc_types.LINK, link_content_2)
        addr_list = client.create_elements(const)
        self.assertTrue(addr_list)
        content = client.get_link_by_content([test_str_1, link_content_2])
        self.assertTrue(content)
        for item in zip(addr_list, content):
            self.assertTrue(item[0].value in [addr.value for addr in item[1]])

    def test_resolve_keynode_not_exist(self):
        params = ScIdtfResolveParams(idtf="my_new_keynode_that_not_exist", type=sc_types.NODE_CONST)
        addr = client.resolve_keynodes([params])
        self.assertNotEqual(addr[0].value, 0)

    def test_resolve_keynode_exist(self):
        params = ScIdtfResolveParams(idtf="technology_OSTIS", type=sc_types.NODE_CONST)
        addr = client.resolve_keynodes([params])
        self.assertNotEqual(addr[0].value, 0)

    def test_find_keynode_not_exist(self):
        params = ScIdtfResolveParams(idtf="my_another_keynode_that_not_exist", type=None)
        addr = client.resolve_keynodes([params])
        self.assertEqual(addr[0].value, 0)

    def test_find_keynode_exist(self):
        params = ScIdtfResolveParams(idtf="nrel_format", type=None)
        addr = client.resolve_keynodes([params])
        self.assertNotEqual(addr[0].value, 0)

    def test_resolve_keynodes_list(self):
        param1 = ScIdtfResolveParams(idtf="my_new_keynode_that_not_exist", type=sc_types.NODE_CONST)
        param2 = ScIdtfResolveParams(idtf="technology_OSTIS", type=sc_types.NODE_CONST)
        param3 = ScIdtfResolveParams(idtf="my_another_keynode_that_not_exist", type=None)
        addrs = client.resolve_keynodes([param1, param2, param3])
        self.assertEqual(len(addrs), 3)
        self.assertNotEqual(addrs[0].value, 0)
        self.assertNotEqual(addrs[1].value, 0)
        self.assertEqual(addrs[2].value, 0)

    def test_create_event(self):
        def test_callback(subscribed_el: ScAddr, edge: ScAddr, init_el: ScAddr):  # pylint: disable=W0613
            params = ScIdtfResolveParams(idtf="test_event_callback", type=sc_types.NODE_CONST)
            client.resolve_keynodes([params])

        params = ScIdtfResolveParams(idtf="my_new_keynode_that_not_exist", type=sc_types.NODE_CONST)
        addr = client.resolve_keynodes([params])
        event_params = ScEventParams(addr[0], common.ScEventType.REMOVE_ELEMENT, test_callback)
        sc_event = client.events_create([event_params])
        self.assertTrue(client.is_event_valid(sc_event[0]))

        # expect empty keynode
        params = ScIdtfResolveParams(idtf="test_event_callback", type=None)
        event_test_addr = client.resolve_keynodes([params])
        client.delete_elements(event_test_addr)
        event_test_addr = client.resolve_keynodes([params])
        self.assertEqual(event_test_addr[0].value, 0)
        # event call
        status = client.delete_elements(addr)
        self.assertTrue(status)

        # expect event create keynode
        time.sleep(0.1)
        params = ScIdtfResolveParams(idtf="test_event_callback", type=None)
        event_test_addr = client.resolve_keynodes([params])
        self.assertNotEqual(event_test_addr[0].value, 0)
        client.delete_elements(event_test_addr)

    def test_create_events_list(self):
        def test_callback_first_node(src: ScAddr, edge: ScAddr, trg: ScAddr):  # pylint: disable=W0613
            params = ScIdtfResolveParams(idtf="test_node", type=None)
            test_node = client.resolve_keynodes([params])
            self.assertNotEqual(test_node[0].value, 0)
            const = ScConstruction()
            const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, trg, test_node[0])
            edge = client.create_elements(const)
            self.assertNotEqual(edge[0].value, 0)

        def test_callback_second_node(src: ScAddr, edge: ScAddr, trg: ScAddr):  # pylint: disable=W0613
            params = ScIdtfResolveParams(idtf="new_test_node", type=sc_types.NODE_CONST)
            client.resolve_keynodes([params])

        params_1 = ScIdtfResolveParams(idtf="first_node", type=sc_types.NODE_CONST)
        params_2 = ScIdtfResolveParams(idtf="second_node", type=sc_types.NODE_CONST)
        params_3 = ScIdtfResolveParams(idtf="test_node", type=sc_types.NODE_CONST)
        addrs = client.resolve_keynodes([params_1, params_2, params_3])
        event_params_1 = ScEventParams(addrs[0], common.ScEventType.ADD_OUTGOING_EDGE, test_callback_first_node)
        event_params_2 = ScEventParams(addrs[1], common.ScEventType.ADD_OUTGOING_EDGE, test_callback_second_node)
        sc_event = client.events_create([event_params_1, event_params_2])
        self.assertTrue(client.is_event_valid(sc_event[0]))
        self.assertTrue(client.is_event_valid(sc_event[1]))
        const = ScConstruction()
        const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, addrs[0], addrs[1])
        client.create_elements(const)

        time.sleep(0.2)
        params = ScIdtfResolveParams(idtf="new_test_node", type=None)
        new_test_node = client.resolve_keynodes([params])
        self.assertNotEqual(new_test_node[0].value, 0)
        for addrs_list in [addrs, new_test_node]:
            client.delete_elements(addrs_list)

    def test_destroy_event(self):
        def test_callback(subscribed_el: ScAddr, edge: ScAddr, init_el: ScAddr):  # pylint: disable=W0613
            pass

        params = ScIdtfResolveParams(idtf="my_new_keynode_that_not_exist", type=sc_types.NODE_CONST)
        addr = client.resolve_keynodes([params])
        event_params = ScEventParams(addr[0], common.ScEventType.REMOVE_ELEMENT, test_callback)
        sc_events = client.events_create([event_params])
        self.assertTrue(client.is_event_valid(sc_events[0]))
        client.events_destroy(sc_events)
        self.assertIsNone(client.is_event_valid(sc_events[0]))
        client.delete_elements(addr)

    def test_destroy_events_list(self):
        def test_callback(subscribed_el: ScAddr, edge: ScAddr, init_el: ScAddr):  # pylint: disable=W0613
            pass

        params_1 = ScIdtfResolveParams(idtf="first_node", type=sc_types.NODE_CONST)
        params_2 = ScIdtfResolveParams(idtf="second_node", type=sc_types.NODE_CONST)
        addrs = client.resolve_keynodes([params_1, params_2])
        event_params_1 = ScEventParams(addrs[0], common.ScEventType.ADD_OUTGOING_EDGE, test_callback)
        event_params_2 = ScEventParams(addrs[1], common.ScEventType.ADD_OUTGOING_EDGE, test_callback)
        sc_events = client.events_create([event_params_1, event_params_2])
        self.assertTrue(client.is_event_valid(sc_events[0]))
        self.assertTrue(client.is_event_valid(sc_events[1]))
        client.events_destroy(sc_events)
        self.assertIsNone(client.is_event_valid(sc_events[0]))
        self.assertIsNone(client.is_event_valid(sc_events[1]))
        client.delete_elements(addrs)

    def test_template_search(self):
        def for_each_tripple_func(src: ScAddr, edge: ScAddr, trg: ScAddr):
            for addr in [src, edge, trg]:
                self.assertTrue(isinstance(addr, ScAddr))

        link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST, "node_1")
        const.create_node(sc_types.NODE_CONST, "node_2")
        const.create_node(sc_types.NODE_CONST_CLASS, "node_3")
        const.create_link(sc_types.LINK, link_content, "link")
        const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, "node_3", "link")
        const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_TEMP, "node_3", "node_1")
        const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_TEMP, "node_3", "node_2")
        addr_list = client.create_elements(const)

        templ = ScTemplate()
        templ.triple([addr_list[2], "_class_node"], sc_types.EDGE_ACCESS_VAR_POS_PERM, addr_list[3])
        templ.triple("_class_node", sc_types.EDGE_ACCESS_VAR_POS_TEMP, addr_list[0])
        templ.triple("_class_node", addr_list[6], sc_types.NODE_VAR)
        templ.triple(addr_list[0], addr_list[6], sc_types.NODE_VAR, is_required=False)
        search_result_list = client.template_search(templ)

        self.assertNotEqual(len(search_result_list), 0)
        search_result = search_result_list[0]
        self.assertEqual(search_result.size(), 12)
        self.assertEqual(search_result.get("_class_node").value, search_result.get(0).value)
        search_result.for_each_triple(for_each_tripple_func)

    def test_template_generate(self):
        const = ScConstruction()
        const.create_node(sc_types.NODE_CONST)
        const.create_node(sc_types.NODE_CONST_NOROLE)
        const.create_node(sc_types.NODE_CONST_CLASS)
        const.create_link(sc_types.LINK, ScLinkContent("Hello!", ScLinkContentType.STRING.value))
        nodes = client.create_elements(const)

        templ = ScTemplate()
        templ.triple_with_relation(
            [nodes[2], "_main_node"],
            sc_types.EDGE_D_COMMON_VAR,
            [sc_types.LINK, "_link"],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            nodes[1],
        )
        templ.triple("_main_node", sc_types.EDGE_ACCESS_VAR_POS_TEMP, [sc_types.NODE_VAR, "_var_node"])

        gen_params = {"_link": nodes[3], "_var_node": nodes[0]}
        gen_result = client.template_generate(templ, gen_params)
        self.assertEqual(gen_result.size(), 9)
