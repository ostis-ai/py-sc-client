# py-sc-client

![Tests badge](https://github.com/ostis-ai/py-sc-client/actions/workflows/tests.yml/badge.svg?branch=main)
![Push badge](https://github.com/ostis-ai/py-sc-client/actions/workflows/push.yml/badge.svg?branch=main)

The python implementation of the client for communication with
[the OSTIS Technology web-oriented platform](https://github.com/ostis-ai/ostis-web-platform/blob/develop/docs/main.pdf).
This library is compatible with `0.10.0` version of [sc-machine](https://github.com/ostis-ai/sc-machine).

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

## Connection to the sc-server

First you need connect to the sc-server.
It's implemented using web-socket in another thread.
Do not forget to disconnect after all operations.

- *sc_client.client*.**connect**(url: str)

Connect to the sc-server by *url*.

```python
from sc_client.client import connect

url = "ws://localhost:8090/ws_json"
connect(url)
```

- *sc_client.client*.**disconnect**()

Close the connection with the sc-server.

```python
from sc_client.client import disconnect

disconnect()
```

- *sc_client.client*.**is_connected**()

Returns boolean state of the connection with the sc-server.

```python
from sc_client.client import is_connected

if is_connected():
    ...
```

- *sc_client.client*.**set_error_handler**(callback)

Sets a handler callback to manage client and server errors. Callback must take one argument - an exception object.

```python
from sc_client.client import set_error_handler

def on_error(e):
    if isinstance(e, AttributeError):
        print(e)

set_error_handler(on_error)        
...
```

- *sc_client.client*.**set_reconnect_handler**(**reconnect_kwargs)

Sets handler callback to reconnect on sc-server connection failure. Method takes the following arguments:
 
- `_reconnect_handler_` - handler callback function. Default value: `_session.default_reconnect_handler_`.
- `_post_reconnect_callback_` - handler callback invoked after `_reconnect_handler_` has finished successfully.
- `_reconnect_retries_` - amount of call tries of `_reconnect_handler_`. Default value: `5`.
- `_reconnect_retry_delay_` - period between call tries of `_reconnect_handler_` (in seconds). Default value: `2`.

If the sc-server did not respond to one of the resent messages, after a requested `_reconnect_retry_delay_`
the `_reconnect_handler_` is called, and the same message is sent again. This procedure is repeated for
`_reconnect_retries_` times, until the message is sent and a response is received.

```python
from sc_client.client import set_reconnect_handler

url = "ws://localhost:8090/ws_json"

def on_reconnect():
    connect(url)

set_reconnect_handler(
    reconnect_handler=connect,
    post_reconnect_handler=None,
    reconnect_retries=5,
    reconnect_retry_delay=1.0 #seconds
)        
...
```

## Base classes

### ScAddr

Minimum element of sc is ScAddr.
It contains address of some element in sc-memory.
Knowing it, you can find related elements, connect connectors, check the type, and so on:

- *sc_client.models*.**ScAddr**

Class with int address and usable methods.
If value is zero (0), ScAddr is invalid (doesn't exist or there is an error).

```python
from sc_client.models import ScAddr

addr = ScAddr(0)
# You can initialize ScAddr, but it's not recommended.
# Usually you will receive valid ones from special functions.

is_valid = addr.is_valid()  # you can check if explicitly
if addr:  # Or implicitly using magic method __bool__()
    ...

assert addr == addr  # You can compare ScAddr with ScAddr if they are equal
assert addr.is_equal(addr)  # Alternative variant
assert addr == 0  # InvalidTypeError
```

### ScType

Every valid sc-element has some type.
Sc-type represents a bit mask. But you don't need to know it.
There is the ScType class that contains all methods to check type.
All common ScTypes like node const are already defined.

- *sc_client.constants*.**ScType**

Class with type of sc-element.
It uses when new elements are created or if it's need to check right type.
It contains methods to check if it is node, connector or link, const or var, and so on.

If you paid attention, the class is in constants submodule.
They are already defined, and you can import them from file `sc_client.constants.sc_type`.
If you need bitmasks, they are in `sc_client.constants.sc_type.bitmasks`.

```python
from sc_client.constants import sc_type

sc_type_structure = sc_type.CONST_NODE_STRUCTURE

assert sc_type_structure.is_valid()

assert sc_type_structure.is_node()
assert not sc_type_structure.is_connector()
assert not sc_type_structure.is_link()

assert sc_type_structure.is_const()
assert not sc_type_structure.is_var()

assert sc_type_structure.is_structure()
assert not sc_type_structure.is_tuple()
# And many more
```

## Structure classes

Structure classes are using to work with set of sc-elements.
ScConstruction uses individual elements like nodes and connectors,
ScTemplate - triplets

### ScConstruction

- *sc_client.models*.**ScConstruction**

Class that allow to create single nodes, connectors and links.
You can use aliases to name nodes, and use one element several times in construction.

Methods:

1. *ScConstruction*.**generate_node**(sc_type: ScType, alias: str = None)
2. *ScConstruction*.**generate_connector**(sc_type: ScType, src: str | ScAddr, trg: str | ScAddr, alias: str = None)
3. *ScConstruction*.**generate_link**(sc_type: ScType, content: ScLinkContent, alias: str = None)

ScConstruction doesn't create elements. To do it use function:

- *sc_client.client*.**generate_elements**(constr: ScConstruction)

It returns list of all elements by ScConstruction *constr*.

```python
from sc_client.client import generate_elements
from sc_client.constants import sc_type
from sc_client.models import ScConstruction
from sc_client.models import ScLinkContent, ScLinkContentType

construction = ScConstruction()  # First you need initialize

construction.generate_node(sc_type.CONST_NODE, 'node')  # Create node const

link_content = ScLinkContent("Hello!", ScLinkContentType.STRING)  # Create link content
construction.generate_link(sc_type.CONST_NODE_LINK, link_content, 'link')  # Create link with that content

construction.generate_connector(sc_type.CONST_PERM_POS_ARC, 'node', 'link')
# Create unaliased connector between previous node

addrs = generate_elements(construction)  # List of elements
assert len(addrs) == 3  # Assert that there is 3 elements as in the construction
assert all(addrs)  # Assert that they are all valid
```

Also, you can generate a construction by template address or its system identifier or scs-template as well as search
constructions.

### ScTemplate

- *sc_client.models*.**ScTemplate**

Class that allow to create and search triplets.
You can also use aliases to name nodes, and use one element several times in template.

Methods:

1. *ScTemplate*.**triple**(source, connector, target)

   Template `source-connector-target`
2. *ScTemplate*.**quintuple**(source, connector, target, attribute_connector, attribute)

   Two triplets `source-connector-target` and `attribute-attribute_connector-connector`

To set aliases use syntax:

- `element >> alias` Recommended
- `(element, alias)`

After setting alias you use it without element

#### Search by template

- *sc_client.client*.**search_by_template**(template: ScTemplate, params: ScTemplateParams = None)

Returns list of ScTemplateResult by *template*.

```python
from sc_client.client import search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScTemplate, ScAddr

action_class_node: ScAddr
action_node: ScAddr
rrel_1: ScAddr
# Some ScAddrs for example

template = ScTemplate()
template.triple(action_class_node, sc_type.VAR_PERM_POS_ARC, action_node >> "_action_node")
# Triple `action_class_node-(*new)membership-arc-(*aliased with "_action_node")action_node`
template.quintuple(
    "_action_node",
    sc_type.VAR_TEMP_POS_ARC,
    sc_type.VAR_NODE >> "_arg_node",
    sc_type.VAR_TEMP_POS_ARC,
    rrel_1,
)

search_results = search_by_template(template)
```

Search by sc-template address.

```python
from sc_client.client import search_by_template
from sc_client.models import ScAddr

template: ScAddr  # Template from sc-memory
search_results = search_by_template(template)
search_result = search_results[0]
```

You can also use ScAddr templates:

Search by sc-template system identifier.

```python
from sc_client.client import search_by_template
from sc_client.models import ScAddr

link_node: ScAddr
search_params = {'_link': link_node, '_var_node': 'node_idtf'}
search_results = search_by_template('my_template', search_params)
search_result = search_results[0]

```

Search by scs sc-template.

```python
from sc_client.client import search_by_template

search_results = search_by_template('class _-> _node;;')
search_result = search_results[0]
```

#### Generate by template

- *sc_client.client*.**generate_by_template**(template: ScTemplate, params: ScTemplateParams = None)

Returns ScTemplateResult by *template*.

```python
from sc_client.client import generate_by_template
from sc_client.constants import sc_type
from sc_client.models import ScTemplate, ScAddr

main_node: ScAddr
relation_node: ScAddr
link_node: ScAddr
# Some ScAddrs for example

template = ScTemplate()
template.quintuple(
    main_node >> '_main_node',
    sc_type.VAR_COMMON_ARC,
    sc_type.VAR_NODE_LINK >> '_link',
    sc_type.VAR_PERM_POS_ARC,
    relation_node,
)
template.triple(
    '_main_node',
    sc_type.VAR_TEMP_POS_ARC,
    sc_type.VAR_NODE >> '_var_node'
)
gen_params = {'_link': link_node, '_var_node': 'node_idtf'}
gen_result = generate_by_template(template, gen_params)
```

Also, you can generate a construction by template address or its system identifier or scs-template as well as search
constructions.

#### ScTemplateResult

After operations with template you'll receive ScTemplateResult:

- *sc_client.models*.**ScTemplateResult**

It has all ScAddr and aliases. You can get addrs or iterate.

Methods:

- **len**(*ScTemplateResult*)

  Get count of elements
- *ScTemplateResult*.**size**()

  Get ScAddr by index
- *ScTemplateResult*.**get**(alias_or_index: str | int)

  Get ScAddr by alias or index
- **iter**(*ScTemplateResult*), **next**(*ScTemplateResult*)


```python
from enum import Enum

from sc_client.models import ScTemplateResult, ScAddr

template_result: ScTemplateResult
length = len(template_result)  # in the resulting construction
first_element = template_result[0]  # get an element from the result by index (recommended)
template_result.get(0)  # get an element from the result by index
arg_node = template_result.get("_arg_node")  # get an element from the result by alias

for src, connector, trg in template_result:
    ...
    # do smth with each triple in the result
```

## Common functions

### Get elements types

- *sc_client.client*.**get_elements_types**(*addrs: ScAddr)

Returns list of ScTypes for given elements.

```python
from sc_client.client import get_elements_types

from sc_client.client import generate_elements
from sc_client.constants import sc_type
from sc_client.models import ScConstruction

construction = ScConstruction()  # Create elements for example
construction.generate_node(sc_type.CONST_NODE)
construction.generate_node(sc_type.VAR_NODE)
elements = generate_elements(construction)

elements_types = get_elements_types(*elements)
assert elements_types[0].is_node()
assert not elements_types[1].is_connector()
assert elements_types[1].is_var()
```

### Generate elements by SCs

- *sc_client.client*.**generate_elements_by_scs**(texts: List[Union[str, SCs]])

Create elements by scs texts in the KB memory,
put them in structure and returns boolean statuses.

```python
from sc_client.client import generate_elements_by_scs

results = generate_elements_by_scs(["concept1 -> node1;;", "concept1 -> ;;"])
assert results == [True, False]  # Warning: it doesn't return False, it raised error
```

```python
from sc_client.client import generate_elements_by_scs, generate_elements
from sc_client.constants import sc_type
from sc_client.models import SCs, ScConstruction

construction = ScConstruction()  # Create output_struct for example
construction.generate_node(sc_type.CONST_NODE)
output_struct = generate_elements(construction)[0]

results = generate_elements_by_scs([SCs("concept1 -> node1;;", output_struct), "concept1 -> node2;;"])
assert results == [True, True]
```

### Erase elements

- *sc_client.client*.**erase_elements**(*addrs: ScAddr)

Erase *addrs* from the KB memory and returns boolean status.

```python
from sc_client.client import generate_elements, set_link_contents
from sc_client.constants import sc_type
from sc_client.models import ScConstruction, ScLinkContent, ScLinkContentType

construction = ScConstruction()  # Create link for example
construction.generate_node(sc_types.CONST_NODE, "node1")
construction.generate_node(sc_types.CONST_NODE, "node2")
construction.generate_node(sc_types.CONST_POS_PERM_ARC, "node1", "node2")
elements = generate_elements(construction)

erase_elements(*elements)
```

### Resolve keynodes

- *sc_client.client*.**resolve_keynodes**(*params: ScIdtfResolveParams)

Resolve keynodes from the KB memory by ScIdtfResolveParams and return list of ScAddrs. If it doesn't exist, then create
a new one.

- *sc_client.models*.**ScIdtfResolveParams**

Typed-dict class that contains *idtf* and optional *type*

***Advice: better to use ScKeynodes from py-sc-kpm***

```python
from sc_client.client import resolve_keynodes
from sc_client.constants import sc_type
from sc_client.models import ScIdtfResolveParams

params = ScIdtfResolveParams(idtf='new_keynode_that_doesnt_exist', type=sc_type.CONST_NODE)
addrs = resolve_keynodes(params)  # list with 1 new keynode addr

params = ScIdtfResolveParams(idtf='keynode_that_have_to_exist_but_doesnt', type=None)
addrs = resolve_keynodes(params)  # list with 1 invalid addr

params = ScIdtfResolveParams(idtf='keynode_that_exists', type=None)
addrs = resolve_keynodes(params)  # list with 1 keynode addr
```

## Link content functions

### ScLinkContent class

- *sc_client.models*.**ScLinkContent**

Class that describes content, its type (enum *sc_client.models*.**ScLinkContentType**).

It uses to create and change links.

```python
from sc_client.models import ScLinkContent, ScLinkContentType, ScAddr

str_content = ScLinkContent("str content", ScLinkContentType.STRING)
int_content = ScLinkContent(12, ScLinkContentType.INT)
float_content = ScLinkContent(3.14, ScLinkContentType.FLOAT)

link_addr: ScAddr  # ScAddr of existed link
link_content = ScLinkContent(12, ScLinkContentType.INT, link_addr)

deprecated_type = ScLinkContent("use enum without .value", ScLinkContentType.STRING.value)
```

### Set links content

- *sc_client.client*.**set_link_contents**(*contents: ScLinkContent)

Set the new content to corresponding links and return boolean status.

```python
from sc_client.client import set_link_contents, generate_elements
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction

construction = ScConstruction()  # Create link for example
link_content1 = ScLinkContent("One", ScLinkContentType.STRING)
construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
link = generate_elements(construction)[0]

link_content2 = ScLinkContent("Two", ScLinkContentType.STRING, link)
status = set_link_contents(link_content2)
assert status
```

### Get links content

- *sc_client.client*.**get_link_contents**(*addr: ScAddr)

Get list of contents of the given links.

```python
from sc_client.client import generate_elements, get_link_content
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction

construction = ScConstruction()  # Create link for example
link_content1 = ScLinkContent("One", ScLinkContentType.STRING)
construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
link = generate_elements(construction)[0]

link_content = get_link_content(link)[0]
assert link_content.data == link_content1.data
```

### Search links by contents

- *sc_client.client*.**search_links_by_contents**(*contents: ScLinkContent | str | int)

Returns list of lists of links for every content.

```python
from sc_client.client import generate_elements, search_links_by_contents
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction

search_string = "search string"

construction = ScConstruction()  # Create link with search string
link_content1 = ScLinkContent(search_string, ScLinkContentType.STRING)
construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
link = generate_elements(construction)[0]

links = search_links_by_contents(search_string)[0]
assert link in links
```

### Search links by content substring

- *sc_client.client*.**search_links_by_contents_substrings**(*contents: ScLinkContent | str | int)

Returns list of lists of links for every content substring.

```python
from sc_client.client import generate_elements, search_links_by_contents_substrings
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction

search_string = "substring1 substring2"

construction = ScConstruction()  # Create link with search string
link_content1 = ScLinkContent(search_string, ScLinkContentType.STRING)
construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
link = generate_elements(construction)[0]

links_list = search_links_by_contents_substrings(*search_string.split(" "))
assert all(link in links for links in links_list)
```

### Search links contents by content substrings

- *sc_client.client*.**search_link_contents_by_content_substrings**(*contents: ScLinkContent | str | int)

Returns list of lists of contents of the given content substrings.
***Warning: it returns int addrs***

```python
from sc_client.client import generate_elements, search_link_contents_by_content_substrings
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction

search_string = "substring1 substring2"

construction = ScConstruction()  # Create link with search string
link_content1 = ScLinkContent(search_string, ScLinkContentType.STRING)
construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
link_addr = generate_elements(construction)[0]

links_list = search_link_contents_by_content_substrings(*search_string.split(" "))
assert all(link_addr.value in links for links in links_list)
```

## Events functions

### Create event subscriptions

- *sc_client.client*.**create_elementary_event_subscriptions**(*event_subscriptions: ScEventSubscriptionParams)

Create an event in the KB memory by ScEventSubscriptionParams and return list of ScEventSubscriptions.

```python
from sc_client.client import event_subscriptions_create
from sc_client.constants.common import ScEventType
from sc_client.models import ScEventSubscriptionParams, ScAddr


def event_callback(src: ScAddr, connector: ScAddr, trg: ScAddr):
    ...


bounded_elem_addr: ScAddr
event_type = ScEventType.AFTER_GENERATE_OUTGOING_ARC
event_subscription_params = ScEventSubscriptionParams(bounded_elem_addr, event_type, event_callback)
event_subscription = create_elementary_event_subscriptions(event_subscription_params)
```

### Check event validity

- *sc_client.client*.**is_event_subscription_valid**(event: ScEventSubscription)

Return boolean status if *event* is active and or not.

*Parameters*: An ScEventSubscription class object.
*Returns*: The boolean value (true if an event is valid).

```python
from sc_client.client import is_event_subscription_valid
from sc_client.models import ScEventSubscription

event_subscription: ScEventSubscription
status = is_event_subscription_valid(event_subscription)
```

### Destroy event subscriptions

- *sc_client.client*.**destroy_elementary_event_subscriptions**(*event_subscriptions: ScEventSubscription)

Destroy *event_subscriptions* in the KB memory and return boolean status.

```python
from sc_client.client import destroy_elementary_event_subscriptions
from sc_client.models import ScEventSubscription

event_subscription: ScEventSubscription
status = destroy_elementary_event_subscriptions(event_subscription)
```

## Classes

***Warning: these classes are deprecated because they are realized in py-sc-kpm.***

The library contains the python implementation of useful classes and functions to work with the sc-memory.

There is a list of classes:

- ScKeynodes

### ScKeynodes

A singleton dictionary object which provides the ability to cache the identifier and ScAddr of keynodes stored in the
KB.
Create an instance of the ScKeynodes class to get access to the cache:

```py
keynodes = ScKeynodes()
```

Get the provided identifier:

```py
keynodes["identifier_of_keynode"]  # returns an ScAddr of the given identifier
keynodes["not_stored_in_kb"]  # returns an invalid ScAddr if an identifier does not exist in the memory
```

Use _resolve_identifiers()_ to upload identifiers from _Enum_ classes:

```py
class CommonIdentifiers(Enum):
    RREL_ONE = "rrel_1"
    RREL_TWO = "rrel_2"


class ActionStatus(Enum):
    ACTION_INITIATED = "action_initiated"
    ACTION_FINISHED = "action_finished"
    ACTION_FINISHED_SUCCESSFULLY = "action_finished_successfully"
    ACTION_FINISHED_UNSUCCESSFULLY = "action_finished_unsuccessfully"


keynodes.resolve_identifiers([ActionStatus, CommonIdentifiers])
```

## Logging

Sometimes you might be in a situation where you deal with data that should be correct, but actually is not.
You may still want to log that something fishy happened. This is where loggers come in handy.
Default logger is preconfigured for you to use.

There is an example for logs review using root logger:

```py
import logging

from sc_client import client

root_logger = logging.getLogger()
root_logger.level = logging.DEBUG
root_logger.addHandler(logging.StreamHandler())

client.connect("ws://localhost:8090/ws_json")
# Connected
result = client.generate_elements_by_scs([])
# Send: {"id": 2, "type": "generate_elements_by_scs", "payload": []}
# Receive: {"errors":[],"event":0,"id":2,"payload":[],"status":1}
client.disconnect()
# Disconnected
```

See [logging documentation](https://docs.python.org/3/library/logging.html#module-logging) for more information.
