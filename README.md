# **py-sc-client** #

<img src="https://github.com/ostis-ai/py-sc-client/actions/workflows/tests.yml/badge.svg?branch=main">
<img src="https://github.com/ostis-ai/py-sc-client/actions/workflows/push.yml/badge.svg?branch=main">

The python implementation of the client for communication with
[the OSTIS Technology web-oriented platform](https://github.com/ostis-ai/ostis-web-platform/blob/develop/docs/main.pdf).
This module is compatible with 0.7.0 version of [sc-machine](https://github.com/ostis-ai/sc-machine).

## Installing py-sc-client
py-sc-client is available on [PyPI](https://pypi.org/project/py-sc-client/):

```sh
$ pip install py-sc-client
```

py-sc-client officially supports Python 3.8+.

## API Reference

### connect
Connect to the server by the URL. Run the client in another thread.

*Parameters*: A URL of the sc-server as a string.

```py
from sc_client import client

client.connect("ws://localhost:8090/ws_json")
```


### disconnect
Close the connection with the sc-server.

```py
from sc_client import client

client.disconnect()
```


### is_connected
Check the state of the connection with the sc-server.

*Returns*: The boolean value (true if a connection is established).

```py
from sc_client import client

client.is_connected() # True
```


### check_elements
Check the type of given elements.

*Parameters*: ScAddr class objects.
*Returns*: A list of ScType class objects.

```py
elem_types = client.check_elements(node_addr, edge_addr, link_addr)
elem_types[0].is_node() #True
elem_types[1].is_edge() #True
elem_types[2].is_link() #True
```


### create_elements
Create a given construction in the KB memory.

*Parameters*: An ScConstruction class object.
*Returns*: A list of ScAddr class objects.

```py
const = ScConstruction()
const.create_node(sc_types.NODE_CONST, 'node')
link_content = ScLinkContent("Hello!", ScLinkContentType.STRING)
const.create_link(sc_types.LINK_CONST, link_content, 'link')
const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, 'node', 'link')
addr_list = client.create_elements(const)
addr_list # [node_addr, link_addr, edge_addr]
```


### create_elements_by_scs
Create elements by scs texts in the KB memory.

*Parameters*: A list of scs (str).
*Returns*: A list of bool scs translation results.

```py
results = client.create_elements_by_scs(["concept1 -> node1;;", "concept1 -> ;;"])
results # [True, False]
```


### delete_elements
Delete elements from the KB memory.

*Parameters*: ScAddr class objects.
*Returns*: The boolean value (true if elements were deleted).

```py
status = client.delete_elements(node_addr, edge_addr, link_addr)
status #True
```


### set_link_contents
Set the new content to corresponding links.

*Parameters*: ScLinkContent class objects.
*Returns*: The boolean value (true if the link content is set).

```py
link_content = ScLinkContent("Hello world!", ScLinkContentType.STRING)
link_content.addr = link_addr
status = client.set_link_contents(link_content)
status # True
```


### get_link_content
Get the content of the given link.

*Parameters*: An ScAddr class object.
*Returns*: A list of ScLinkContent class objects.

```py
link_content = client.get_link_content(link_addr)
link_content[0].data # link content
link_content[0].addr # link addr
```


### get_links_by_content
Get links from the KB with content.

*Parameters*: ScLinkContent class objects, strings.
*Returns*: A list of lists of ScAddr class objects.

```py
content = client.get_links_by_content("testing search by the link content as a string", "no content")
content[0]  # get a list of ScAddrs links with the given content
content[1]  # get an empty list if there is no link with the given content in the memory
```


### get_links_by_content_substring
Get links from the KB by content substring.

*Parameters*: ScLinkContent class objects, substrings.
*Returns*: A list of lists of ScAddr class objects.

```py
content = client.get_links_by_content_substring("testing search", "no con")
content[0]  # get a list of ScAddrs links with the given content substring
content[1]  # get an empty list if there is no link with the given content substring in the memory
```


### resolve_keynodes
Get a keynode from the KB memory by identifier and type. If it doesn't exist, then create a new one.
If ScType is None, try to find an element by the system identifier.

*Parameters*: An ScIdtfResolveParams class object.
*Returns*: A list of ScAddr class objects.

```py
params = ScIdtfResolveParams(idtf='my_new_keynode_that_not_exist', type=sc_types.NODE_CONST)
addr = client.resolve_keynodes([params])
addr # list with new keynode addr

params = ScIdtfResolveParams(idtf='technology_OSTIS', type=sc_types.NODE_CONST)
addr = client.resolve_keynodes([params])
addr # list with keynode addr

params = ScIdtfResolveParams(idtf='my_another_keynode_that_not_exist', type=None)
addr = client.resolve_keynodes([params])
addr # list with invalid addr

params = ScIdtfResolveParams(idtf='nrel_format', type=None)
addr = client.resolve_keynodes([params])
addr # list with keynode addr
```


### template_search
Search in the KB memory by template.

*Parameters*: An ScTemplate class object or a scs-template as a string, an ScTemplateParams class object.
*Returns*: A list of ScTemplateResult class objects.

ScTemplateParams may contain addresses of sc-elements or system identifiers of them.

```py
templ = ScTemplate()
templ.triple([class_node_addr, '_class_node'], sc_types.EDGE_ACCESS_VAR_POS_PERM, node_addr) # faf
templ.triple('_class_node', sc_types.EDGE_ACCESS_VAR_POS_TEMP, link_addr) # faf
templ.triple('_class_node', edge_addr, sc_types.NODE_VAR) # ffa
templ.triple(node_addr, edge_addr, sc_types.NODE_VAR) # ffa

search_params = {'_link': link_node, '_var_node': 'node_idtf'} # value element can be ScAddr or str
search_results = client.template_search(templ, search_params) # templ can be ScTemplate or ScTemplateIdtf or ScAddr
search_result = search_results[0]

search_result.size() # count of elements in the resulting construction
search_result.get(0).value # get an element from the result by index
search_result.get('_class_node').value # get an element from the result by alias

def for_each_tripple_func(src: ScAddr, edge: ScAddr, trg: ScAddr):
    ...
search_result.for_each_triple(for_each_tripple_func) # call a function for each triple in the result
```

Search by sc-template address.
```py
template = keynodes['my_template']
search_results = client.template_search(template)
search_result = search_results[0]

search_result.size()
```

Search by sc-template system identifier.
```py
search_params = {'_link': link_node, '_var_node': 'node_idtf'}
search_results = client.template_search('my_template', search_params)
search_result = search_results[0]

search_result.size()
```

Search by scs sc-template.
```py
search_results = client.template_search('class _-> _node;;')
search_result = search_results[0]

search_result.size()
```

### template_generate
Generate a construction in the KB memory by template.

*Parameters*: An ScTemplate class object or a scs-template as a string, an ScTemplateParams class object.
*Returns*: An ScTemplateResult class object.

```py
templ = ScTemplate()
templ.triple_with_relation( # faaaf
    [main_node, '_main_node'],
    sc_types.EDGE_D_COMMON_VAR,
    [sc_types.LINK_VAR, '_link'],
    sc_types.EDGE_ACCESS_VAR_POS_PERM,
    relation_node,
)
templ.triple( # faa
    '_main_node',
    sc_types.EDGE_ACCESS_VAR_POS_TEMP,
    [sc_types.NODE_VAR, '_var_node']
)
gen_params = {'_link': link_node, '_var_node': 'node_idtf'}
gen_result = client.template_generate(templ, gen_params)
```

Also, you can generate a construction by template address or its system identifier or scs-template as well as search constructions.

### events_create
Create an event in the KB memory.

*Parameters*: ScEventParams class objects.
*Returns*: A list of ScEvent class objects.

```py
def event_callback(src: ScAddr, edge: ScAddr, trg: ScAddr):
    ...

event_type = common.ScEventType.ADD_OUTGOING_EDGE
event_params = ScEventParams(bounded_elem_addr, event_type, event_callback)
sc_event = client.events_create(event_params)
```


### is_event_valid
Check whether an event is active or not.

*Parameters*: An ScEvent class object.
*Returns*: The boolean value (true if an event is valid).

```py
status = client.is_event_valid(sc_event)
status # True
```


### events_destroy
Destroy an event in the KB memory.

*Parameters*: ScEvent class objects.
*Returns*: The boolean value (true if an event was destroyed).

```py
status = client.events_destroy(sc_event)
status # true
```


## Classes
The library contains the python implementation of useful classes and functions to work with the sc-memory.

There is a list of classes:

 - ScKeynodes
 - ScAgent
 - ScModule


### ScKeynodes
A singleton dictionary object which provides the ability to cache the identifier and ScAddr of keynodes stored in the KB.
Create an instance of the ScKeynodes class to get access to the cache:

```py
keynodes = ScKeynodes()
```

Get the provided identifier:
```py
keynodes["identifier_of_keynode"] # returns an ScAddr of the given identifier
keynodes["not_stored_in_kb"] # returns an invalid ScAddr if an identifier does not exist in the memory
```

Use _resolve_identifiers()_ to upload identifiers from _Enum_ classes:

```py
class CommonIdentifiers(Enum):
    RREL_ONE = "rrel_1"
    RREL_TWO = "rrel_2"

class QuestionStatus(Enum):
    QUESTION_INITIATED = "question_initiated"
    QUESTION_FINISHED = "question_finished"
    QUESTION_FINISHED_SUCCESSFULLY = "question_finished_successfully"
    QUESTION_FINISHED_UNSUCCESSFULLY = "question_finished_unsuccessfully"

keynodes.resolve_identifiers([QuestionStatus, CommonIdentifiers])
```


### ScAgent
A class for handling a single ScEvent. Define your agents like this:
```py
class MyAgent(ScAgent):
    action = "Identifier_of_action_class"

    def register(self) -> ScEvent:
        # override method, must return an ScEvent instance
        params = [
            MyAgent.keynodes["action_initiated"],
            common.ScEventType.ADD_OUTGOING_EDGE,
            MyAgent.run_impl
        ]
        event_params = ScEventParams(*params)
        sc_event = client.events_create(event_params)
        return sc_event[0]

    @staticmethod
    def run_impl(action_class: ScAddr, edge: ScAddr, action_node: ScAddr) -> None:
        # override method, must have 3 args and be static
        ...

```


### ScModule
A class for handling a multiple ScAgent. Define your modules like this:
```py
class MyModule(ScModule):
    def __init__(self) -> None:
        agents_to_register = [MyAgent1, MyAgent2] # list of agent classes
        super().__init__(agents_to_register)
```

## Logging

Sometimes you might be in a situation where you deal with data that should be correct, but actually is not.
You may still want to log that something fishy happened. This is where loggers come in handy.
Default logger is preconfigured for you to use.

Here are some example for logs review:
```py
from sc_client import LOGGER_NAME
from sc_client import client
import logging
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG)
client.connect("ws://localhost:8090/ws_json")
# 2022-09-14 13:44:00,667 - py-sc-client - DEBUG - Connected
result = client.create_elements_by_scs([])
# 2022-09-14 13:48:54,776 - py-sc-client - DEBUG - Send: {"id": 2, "type": "create_elements_by_scs", "payload": []}
# 2022-09-14 13:48:54,777 - py-sc-client - DEBUG - Receive: {"errors":[],"event":0,"id":2,"payload":[],"status":1}
```

The attached logger is a standard logging [Logger](https://docs.python.org/3/library/logging.html#logging.Logger),
so head over to the official [logging docs](https://docs.python.org/3/library/logging.html#module-logging)
for more information.
