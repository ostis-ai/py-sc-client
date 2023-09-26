# py-sc-client

[![PyPI Latest](https://img.shields.io/pypi/v/py-sc-client)](https://pypi.org/project/py-sc-client/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-sc-client)
![Tests badge](https://github.com/ostis-ai/py-sc-client/actions/workflows/tests.yml/badge.svg?branch=main)
![Push badge](https://github.com/ostis-ai/py-sc-client/actions/workflows/push.yml/badge.svg?branch=main)

The python implementation of the client for communication with
[the OSTIS Technology web-oriented platform](https://github.com/ostis-ai/ostis-web-platform/blob/develop/docs/main.pdf).
This library is compatible with `0.7.0` version of [sc-machine](https://github.com/ostis-ai/sc-machine).

Low-level functionality implemented in **[py-sc-client](https://github.com/ostis-ai/py-sc-client)**:

- ScAddr
- ScType
- ScStructure
- ScTemplate.

High-level functionality implemented in **[py-sc-kpm](https://github.com/ostis-ai/py-sc-kpm)**:

- ScKeynodes
- ScAgent
- ScModule
- ScServer

## Installation py-sc-client

py-sc-client is available on [PyPI](https://pypi.org/project/py-sc-client/):

```sh
$ pip install py-sc-client
```

py-sc-client officially supports Python 3.8+.

# ScClient & AScClient

The user interacts with py-sc-client using common classes that include needed methods.
There are two types of implementation: synchronous and asynchronous.
Synchronous one uses asynchronous inside.

- *sc_client.core*.**ScClient**
- *sc_client.core*.**AScClient**

You need to initialize `ScClient` or `AScClient` and use their methods, or
use global instances like in version `0.3.0` and earlier in `sc_client.core.(a)sc_client_instance`.

## Connection to the sc-server

First, you need to connect to the sc-server.
It's implemented using web-socket in another task.

- *ScClient*.**connect**(url: str)
- coroutine *AScClient*.**connect**(url: str)

**Connect to the sc-server by *url*.**

Then you can check the connection:

- *ScClient*.**is_connected**()  -> *bool*
- *AScClient*.**is_connected**() -> *bool*

**Return the status of the connection**

Do not forget to disconnect after all operations.

- *ScClient*.**disconnect**()
- coroutine *AScClient*.**disconnect**()

**Close the connection with the sc-server.**

Example of sync ScClient connection:

```python
from sc_client.core.sc_client_instance import sc_client


def main():
    sc_client.connect("ws://localhost:8090/ws_json")
    try:
        print(f"1. {sc_client.is_connected()=}")  # 1. client.is_connected()=True
    finally:
        sc_client.disconnect()
        print(f"2. {sc_client.is_connected()=}")  # 2. client.is_connected()=False


if __name__ == "__main__":
    main()
```

Asynchronous version:

```python
import asyncio

from sc_client.core import AScClient


async def main():
    client = AScClient()
    await client.connect("ws://localhost:8090/ws_json")
    try:
        print(f"1. {client.is_connected()=}")  # 1. client.is_connected()=True
    finally:
        await client.disconnect()
        print(f"2. {client.is_connected()=}")  # 2. client.is_connected()=False


if __name__ == "__main__":
    asyncio.run(main())
```

## Handlers and reconnect settings

You can set handlers on open/close connection, on reconnecting and on error.
AScClient receivers async functions, ScClient - sync

- *ScClient*.**set_on_open_handler**(on_open: Callable[[], None])
- *ScClient*.**set_on_close_handler**(on_close: Callable[[], None])
- *ScClient*.**set_on_error_handler**(on_error: Callable[[Exception], None])
- *ScClient*.**set_on_reconnect_handler**(on_reconnect: Callable[[], None])


- *AScClient*.**set_on_open_handler**(on_open: Callable[[], Awaitable[None]])
- *AScClient*.**set_on_close_handler**(on_close: Callable[[], Awaitable[None]])
- *AScClient*.**set_on_error_handler**(on_error: Callable[[Exception], Awaitable[None]])
- *AScClient*.**set_on_reconnect_handler**(on_reconnect: Callable[[], Awaitable[None]])

On open handler runs after any connection (before on_reconnect if it's successful).
On close handler runs after disconnecting and losing connection.
On error handler runs if sc-server returns response with an error.
On reconnect handler runs after connection restoration (and on_open handler).

Example of setting on_open and on_close handlers:

```python
import logging

from sc_client.core import ScClient

logging.basicConfig(level=logging.INFO)


def on_open():
    logging.info("Callback on open")


def on_close():
    logging.info("Callback on close")


def main():
    client = ScClient()
    client.set_on_open_handler(on_open)
    client.set_on_close_handler(on_close)
    client.connect("ws://localhost:8090/ws_json")  # INFO:root:Callback on open
    try:
        ...
    finally:
        client.disconnect()  # INFO:root:Callback on close


if __name__ == "__main__":
    main()
```

Asynchronous version:

```python
import asyncio
import logging

from sc_client.core import AScClient

logging.basicConfig(level=logging.INFO)


async def on_open():
    logging.info("Callback on open")


async def on_close():
    logging.info("Callback on close")


async def main():
    client = AScClient()
    client.set_on_open_handler(on_open)
    client.set_on_close_handler(on_close)
    await client.connect("ws://localhost:8090/ws_json")  # INFO:root:Callback on open
    try:
        ...
    finally:
        await client.disconnect()  # INFO:root:Callback on close


if __name__ == "__main__":
    asyncio.run(main())
```

You can also set reconnect setting: number of retries and delay between them.

- *ScClient*.**set_reconnect_settings**(retries: int = None, retry_delay: float = None)
- *AScClient*.**set_reconnect_settings**(retries: int = None, retry_delay: float = None)

Default values are stored in *sc_client.constants.config*:

- SERVER_RECONNECT_RETRIES = 5
- SERVER_RECONNECT_RETRY_DELAY = 2.0

## Base classes

### ScAddr

Minimum element of sc is ScAddr.
It contains the address of some elements in sc-memory.
Knowing it, you can find related elements, connect edges, check the type, and so on:

- *sc_client.models*.**ScAddr**

Class with int address and usable methods.
If the value is zero (0), ScAddr is invalid (doesn't exist, or there is an error).

```python
from sc_client.models import ScAddr

addr = ScAddr(0)
# You can initialize ScAddr, but it's not recommended.
# Usually, you will receive valid ones from special functions.

is_valid = addr.is_valid()  # you can check if explicitly
if addr:  # Or implicitly using magic method __bool__()
    ...

assert addr == addr  # You can compare ScAddr with ScAddr if they are equal
assert addr.is_equal(addr)  # Alternative variant
assert addr == 0  # InvalidTypeError
```

### ScType

Every valid sc-element has some type.
Sc-type represents a bitmask, but you don't need to know it.
There is the ScType class that contains all methods to check the type.
All common ScTypes like node const are already defined.

- *sc_client.constants*.**ScType**

Class with the type of sc-element.
It uses when new elements are created or if it's needed to check the right type.
It contains methods to check if it is a node, edge or link, const or var, and so on.

If you paid attention, the class is in constants submodule.
They are already defined, and you can import them from file `sc_client.constants.sc_types`.
If you need bitmasks, they are in `sc_client.constants.bitmasks`.

```python
from sc_client.constants import sc_types

sc_type_struct = sc_types.NODE_CONST_STRUCT

assert sc_type_struct.is_valid()

assert sc_type_struct.is_node()
assert not sc_type_struct.is_edge()
assert not sc_type_struct.is_link()

assert sc_type_struct.is_const()
assert not sc_type_struct.is_var()

assert sc_type_struct.is_struct()
assert not sc_type_struct.is_tuple()
# And many more
```

## Structure classes

Structure classes are used to work with many sc-elements.
ScConstruction uses individual elements such as nodes and edges.
ScTemplate uses triples to search or generate complex structure.

### ScConstruction

- *sc_client.models*.**ScConstruction**

Class that allow to create single nodes, edges, and links.
You can use aliases to name nodes, and use one element several times in construction.

Methods:

1. *ScConstruction*.**create_node**(sc_type: ScType, alias: str = None)
2. *ScConstruction*.**create_edge**(sc_type: ScType, src: str | ScAddr, trg: str | ScAddr, alias: str = None)
3. *ScConstruction*.**create_link**(sc_type: ScType, content: ScLinkContent, alias: str = None)

ScConstruction doesn't create elements. To do it use function:

- *ScClient*.**create_elements**(constr: ScConstruction)
- coroutine *AScClient*.**create_elements**(constr: ScConstruction)

It returns a list of all elements by ScConstruction *constr*.

```python
from sc_client.constants import sc_types
from sc_client.models import ScConstruction
from sc_client.models import ScLinkContent, ScLinkContentType

from sc_client.core.sc_client_instance import sc_client

construction = ScConstruction()  # First, you need to initialize

construction.create_node(sc_types.NODE_CONST, 'node')  # Create node const

link_content = ScLinkContent("Hello!", ScLinkContentType.STRING)  # Create link content
construction.create_link(sc_types.LINK_CONST, link_content, 'link')  # Create a link with that content

construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, 'node', 'link')
# Create unaliased edge between previous node

addrs = sc_client.create_elements(construction)  # List of elements
assert len(addrs) == 3  # Assert that there are three elements as in the construction
assert all(addrs)  # Assert that they are all valid
```

Also, you can generate a construction by template address or its system identifier or scs-template as well as search
constructions.

### ScTemplate

- *sc_client.models*.**ScTemplate**

Class that allow to create and search triplets.
You can also use aliases to name nodes, and use one element several times in template.

Methods:

1. *ScTemplate*.**triple**(src, edge, trg)

   Template `src-edge-trg`
2. *ScTemplate*.**triple_with_relation**(src, edge, trg, edge2, src2)

   Two triplets `src-edge-trg` and `src2-edge2-edge`

To set aliases use syntax:

- `element >> alias` Recommended
- `(element, alias)`

After setting alias, you use it without an element

#### Search template

- *ScClient*.**template_search**(template: ScTemplate, params: ScTemplateParams = None)
- coroutine *AScClient*.**template_search**(template: ScTemplate, params: ScTemplateParams = None)

Returns list of ScTemplateResult by *template*.

```python
from sc_client.constants import sc_types
from sc_client.models import ScTemplate, ScAddr

from sc_client.core.sc_client_instance import sc_client

action_node: ScAddr
question_node: ScAddr
rrel_1: ScAddr
# Some ScAddrs, for example

template = ScTemplate()
template.triple(question_node, sc_types.EDGE_ACCESS_VAR_POS_PERM, action_node >> "_action_node")
# Triple `question_node-(*new)edge_access-(*aliased with "_action_node")action_node`
template.triple_with_relation(
    "_action_node",
    sc_types.EDGE_ACCESS_VAR_POS_TEMP,
    sc_types.NODE_VAR >> "_arg_node",
    sc_types.EDGE_ACCESS_VAR_POS_TEMP,
    rrel_1,
)

search_results = sc_client.template_search(template)
```

Search by sc-template address.

```python
from sc_client.models import ScAddr

from sc_client.core.sc_client_instance import sc_client

template: ScAddr  # Template from sc-memory
search_results = sc_client.template_search(template)
search_result = search_results[0]
```

You can also use ScAddr templates:

Search by sc-template system identifier.

```python
from sc_client.models import ScAddr

from sc_client.core.sc_client_instance import sc_client

link_node: ScAddr
search_params = {'_link': link_node, '_var_node': 'node_idtf'}
search_results = sc_client.template_search('my_template', search_params)
search_result = search_results[0]

```

Search by scs-template.

```python
from sc_client.core.sc_client_instance import sc_client

search_results = sc_client.template_search('class _-> _node;;')
search_result = search_results[0]
```

#### Generate template

- *ScClient*.**template_generate**(template: ScTemplate, params: ScTemplateParams = None)
- coroutine *AScClient*.**template_generate**(template: ScTemplate, params: ScTemplateParams = None)

Returns ScTemplateResult by *template*.

```python
from sc_client.constants import sc_types
from sc_client.models import ScTemplate, ScAddr

from sc_client.core.sc_client_instance import sc_client

main_node: ScAddr
relation_node: ScAddr
link_node: ScAddr
# Some ScAddrs, for example

template = ScTemplate()
template.triple_with_relation(
    main_node >> '_main_node',
    sc_types.EDGE_D_COMMON_VAR,
    sc_types.LINK_VAR >> '_link',
    sc_types.EDGE_ACCESS_VAR_POS_PERM,
    relation_node,
)
template.triple(
    '_main_node',
    sc_types.EDGE_ACCESS_VAR_POS_TEMP,
    (sc_types.NODE_VAR, '_var_node')
)
gen_params = {'_link': link_node, '_var_node': 'node_idtf'}
gen_result = sc_client.template_generate(template, gen_params)
```

Also, you can generate a construction by template address or its system identifier or scs-template as well as search
constructions.

#### ScTemplateResult

After operations with template, you'll receive ScTemplateResult:

- *sc_client.models*.**ScTemplateResult**

It has all ScAddr and aliases. You can get addrs or iterate.

Methods:

- **len**(*ScTemplateResult*)

  Get count of elements
- *ScTemplateResult*[i: int]

  Get ScAddr by index
- *ScTemplateResult*.**get**(alias_or_index: str | int)

  Get ScAddr by alias or index
- **iter**(*ScTemplateResult*), **next**(*ScTemplateResult*)

  Iterate by triplets

```python
from sc_client.models import ScTemplateResult

template_result: ScTemplateResult
length = len(template_result)  # in the resulting construction
first_element = template_result[0]  # get an element from the result by index (recommended)
template_result.get(0)  # get an element from the result by index
arg_node = template_result.get("_arg_node")  # get an element from the result by alias

for src, edge, trg in template_result:
    ...
    # do smth with each triple in the result
```

## Common functions

### Check element types

- *ScClient*.**check_elements**(*addrs: ScAddr)
- coroutine *AScClient*.**check_elements**(*addrs: ScAddr)

Returns list of ScTypes for given elements.

```python
from sc_client.core.sc_client_instance import sc_client

from sc_client.constants import sc_types
from sc_client.models import ScConstruction

construction = ScConstruction()  # Create elements, for example
construction.create_node(sc_types.NODE_CONST)
construction.create_node(sc_types.NODE_VAR)
elements = sc_client.create_elements(construction)

elements_types = sc_client.check_elements(*elements)
assert elements_types[0].is_node()
assert not elements_types[1].is_edge()
assert elements_types[1].is_var()
```

### Create elements by SCS

- *ScClient*.**create_elements_by_scs**(texts: List[Union[str, SCs]])
- coroutine *AScClient*.**create_elements_by_scs**(texts: List[Union[str, SCs]])

Create elements by scs texts in the KB memory, put them in structure and return boolean statuses.

```python
from sc_client.core.sc_client_instance import sc_client

results = sc_client.create_elements_by_scs(["concept1 -> node1;;", "concept1 -> ;;"])
assert results == [True, False]  # Warning: it doesn't return False, it raised error
```

```python
from sc_client.core.sc_client_instance import sc_client

from sc_client.constants import sc_types
from sc_client.models import ScConstruction, SCs

construction = ScConstruction()  # Create output_struct, for example
construction.create_node(sc_types.NODE_CONST)
output_struct = sc_client.create_elements(construction)[0]

results = sc_client.create_elements_by_scs([SCs("concept1 -> node1;;", output_struct), "concept1 -> node2;;"])
assert results == [True, True]
```

### Delete elements

- *ScClient*.**delete_elements**(*addrs: ScAddr)
- coroutine *AScClient*.**delete_elements**(*addrs: ScAddr)

Delete *addrs* from the KB memory and returns boolean status.

```python
from sc_client.core.sc_client_instance import sc_client

from sc_client.constants import sc_types
from sc_client.models import ScConstruction, ScLinkContent, ScLinkContentType

construction = ScConstruction()  # Create a link for example
construction.create_link(sc_types.LINK_CONST, ScLinkContent("One", ScLinkContentType.STRING))
link = sc_client.create_elements(construction)[0]

link_content = ScLinkContent("Two", ScLinkContentType.STRING, link)
status = sc_client.set_link_contents(link_content)
assert status
```

### Resolve keynodes

- *ScClient*.**resolve_keynodes**(*params: ScIdtfResolveParams)
- coroutine *AScClient*.**resolve_keynodes**(*params: ScIdtfResolveParams)

Resolve keynodes from the KB memory by ScIdtfResolveParams and return list of ScAddrs. If it doesn't exist, then create
a new one.

- *sc_client.models*.**ScIdtfResolveParams**

Typed-dict class that contains *idtf* and optional *type*

***Advice: better to use ScKeynodes from py-sc-kpm***

```python
from sc_client.constants import sc_types
from sc_client.models import ScIdtfResolveParams

from sc_client.core.sc_client_instance import sc_client

params = ScIdtfResolveParams(idtf='new_keynode_that_doesnt_exist', type=sc_types.NODE_CONST)
addrs = sc_client.resolve_keynodes(params)  # list with 1 new keynode addr

params = ScIdtfResolveParams(idtf='keynode_that_have_to_exist_but_doesnt', type=None)
addrs = sc_client.resolve_keynodes(params)  # list with 1 invalid addr

params = ScIdtfResolveParams(idtf='keynode_that_exists', type=None)
addrs = sc_client.resolve_keynodes(params)  # list with 1 keynode addr
```

## Link content functions

### ScLinkContent class

- *sc_client.models*.**ScLinkContent**

Class that describes content, its type (enum *sc_client.models*.**ScLinkContentType**).

It used to create and change links.

```python
from sc_client.models import ScLinkContent, ScLinkContentType, ScAddr

str_content = ScLinkContent("str content", ScLinkContentType.STRING)
int_content = ScLinkContent(12, ScLinkContentType.INT)
float_content = ScLinkContent(3.14, ScLinkContentType.FLOAT)

link_addr: ScAddr  # ScAddr of an existed link
link_content = ScLinkContent(12, ScLinkContentType.INT, link_addr)

deprecated_type = ScLinkContent("use enum without .value", ScLinkContentType.STRING.value)
# Value type is deprecated and will be removed in version 0.3.0
```

### Set links content

- *ScClient*.**set_link_contents**(*contents: ScLinkContent)
- coroutine *AScClient*.**set_link_contents**(*contents: ScLinkContent)

Set the new content to corresponding links and return boolean status.

```python
from sc_client.constants import sc_types
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction

from sc_client.core.sc_client_instance import sc_client

construction = ScConstruction()  # Create a link, for example
link_content1 = ScLinkContent("One", ScLinkContentType.STRING)
construction.create_link(sc_types.LINK_CONST, link_content1)
link = sc_client.create_elements(construction)[0]

link_content2 = ScLinkContent("Two", ScLinkContentType.STRING, link)
status = sc_client.set_link_contents(link_content2)
assert status
```

### Get links content

- *ScClient*.**get_link_contents**(*addr: ScAddr)
- coroutine *AScClient*.**get_link_contents**(*addr: ScAddr)

Get a content list of the given links.

```python
from sc_client.constants import sc_types
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction

from sc_client.core.sc_client_instance import sc_client

construction = ScConstruction()  # Create a link for example
link_content1 = ScLinkContent("One", ScLinkContentType.STRING)
construction.create_link(sc_types.LINK_CONST, link_content1)
link = sc_client.create_elements(construction)[0]

link_content = sc_client.get_link_content(link)[0]
assert link_content.data == link_content1.data
```

### Get links by content

- *ScClient*.**get_links_by_content**(*contents: ScLinkContent | str | int)
- coroutine *AScClient*.**get_links_by_content**(*contents: ScLinkContent | str | int)

Get a nested list of links for every content.

```python
from sc_client.constants import sc_types
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction

from sc_client.core.sc_client_instance import sc_client

search_string = "search string"

construction = ScConstruction()  # Create a link with search string
link_content1 = ScLinkContent(search_string, ScLinkContentType.STRING)
construction.create_link(sc_types.LINK_CONST, link_content1)
link = sc_client.create_elements(construction)[0]

links = sc_client.get_links_by_content(search_string)[0]
assert link in links
```

### Get links by content substring

- *ScClient*.**get_links_by_content_substring**(*contents: ScLinkContent | str | int)
- coroutine *AScClient*.**get_links_by_content_substring**(*contents: ScLinkContent | str | int)

Get a nested list of links for every content substring.

```python
from sc_client.constants import sc_types
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction

from sc_client.core.sc_client_instance import sc_client

search_string = "substring1 substring2"

construction = ScConstruction()  # Create a link with search string
link_content1 = ScLinkContent(search_string, ScLinkContentType.STRING)
construction.create_link(sc_types.LINK_CONST, link_content1)
link = sc_client.create_elements(construction)[0]

links_list = sc_client.get_links_by_content_substring(*search_string.split(" "))
assert all(link in links for links in links_list)
```

### Get links contents by content substring

- *ScClient*.**get_links_contents_by_content_substring**(*contents: ScLinkContent | str | int)
- coroutine *AScClient*.**get_links_contents_by_content_substring**(*contents: ScLinkContent | str | int)

Get a nested list of links for the given content substrings.

```python
from sc_client.constants import sc_types
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction

from sc_client.core.sc_client_instance import sc_client

search_string = "substring1 substring2"

construction = ScConstruction()  # Create a link with search string
link_content1 = ScLinkContent(search_string, ScLinkContentType.STRING)
construction.create_link(sc_types.LINK_CONST, link_content1)
link_addr = sc_client.create_elements(construction)[0]

links_list = sc_client.get_links_contents_by_content_substring(*search_string.split(" "))
assert all(link_addr.value in links for links in links_list)
```

## Events functions

### Create events

- *ScClient*.**events_create**(*events: ScEventParams)
- coroutine *AScClient*.**events_create**(*events: AScEventParams)

Create an event in the KB memory by ScEventParams and return list of ScEvents.

```python
from sc_client.constants.common import ScEventType
from sc_client.models import ScEventParams, ScAddr

from sc_client.core.sc_client_instance import sc_client


def event_callback(src: ScAddr, edge: ScAddr, trg: ScAddr):
    ...


bounded_elem_addr: ScAddr
event_type = ScEventType.ADD_OUTGOING_EDGE
event_params = ScEventParams(bounded_elem_addr, event_type, event_callback)
sc_event = sc_client.events_create(event_params)
```

### Check event validity

- *ScClient*.**is_event_valid**(event: ScEvent)
- *AScClient*.**is_event_valid**(event: AScEvent)

Return boolean status if *event* is active and or not.

*Parameters*: An ScEvent class object.
*Returns*: The boolean value (true if an event is valid).

```python
from sc_client.models import ScEvent

from sc_client.core.sc_client_instance import sc_client

sc_event: ScEvent
status = sc_client.is_event_valid(sc_event)
```

### Destroy events

- *ScClient*.**events_destroy**(*events: ScEvent)
- coroutine *AScClient*.**events_destroy**(*events: AScEvent)

Destroy *events* in the KB memory and return boolean status.

```python
from sc_client.models import ScEvent

from sc_client.core.sc_client_instance import sc_client

sc_event: ScEvent
status = sc_client.events_destroy(sc_event)
```

# Logging

Sometimes you might be in a situation where you deal with data that should be correct, but actually is not.
You may still want to log that something fishy happened. This is where loggers come in handy.
Default logger is preconfigured for you to use.

There is an example for logs review using root logger:

```py
import logging

from sc_client import ScConstruction
from sc_client.constants import sc_types
from sc_client.core import ScClient

root_logger = logging.getLogger()
root_logger.level = logging.DEBUG
root_logger.addHandler(logging.StreamHandler())

client = ScClient()
client.connect("ws://localhost:8090/ws_json")
# Connection opened
constr = ScConstruction()
constr.create_node(sc_types.NODE_CONST)
result = client.create_elements(constr)
# Send: {"id": 2, "type": "create_elements", "payload": ...}
# Receive: {"errors":[],"event":0,"id":1,"payload":[262170],"status":1}
client.disconnect()
# Connection closed
```

See [logging documentation](https://docs.python.org/3/library/logging.html#module-logging) for more information.

# Testing

There is the ability to test sc-client-based projects without real connection to sc-server.
You can emulate responses from sc-server using the websocket patching:

Patch the test class, function or setUp method:
`@patch("websockets.client.connect", websockets_client_connect_patch)`.
Then you need to initialize a client and get its websocket stub.
You can add a message response using ResponseCallback and methods:

- *WebsocketStub*.**sync_set_message_callback**(callback: ResponseCallback)
- coroutine *WebsocketStub*.**set_message_callback**(callback: ResponseCallback)

It adds response callback to the queue

```python
from unittest import TestCase
from unittest.mock import patch

from sc_client import ScAddr, ScType
from sc_client.core import ScClient
from sc_client.testing import SimpleResponseCallback, WebsocketStub, websockets_client_connect_patch


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

    def test_check_elements(self):
        self.websocket.sync_set_message_callback(SimpleResponseCallback(True, False, [11, 22], None))
        results = self.client.check_elements(ScAddr(1), ScAddr(2))
        self.assertEqual(results, [ScType(11), ScType(22)])
```

Check the other variants of testing here:

- [Sync testing](./examples/sync_testing.py)
- [Async testing](./examples/async_testing.py)
