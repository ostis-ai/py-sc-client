# **py-sc-client** #

Python implementation of client for [communication with sc-server](http://ostis-dev.github.io/sc-machine/http/websocket/). This module is tested on Python 3.8+.

Require *websocket-client* library.
```sh
pip3 install websocket-client
```

## connect
Connect to server by url. Run client in another thread. Can be stopped only by interrupt

*Parametrs*: url of sc-server.


```py
from sc_client import client

client.connect("ws://localhost:8090/ws_json")
```



## check_elements
Check type of given elements.

*Parametrs*: list of ScAddr.
*Returns*: ScType of elements.

```py
    elem_types = client.check_elements([node_addr, edge_addr, link_addr])
    elem_types[0].is_node() #True
    elem_types[1].is_edge() #True
    elem_types[2].is_link() #True
```


## create_elements
Create given construction in KB memory.

*Parametrs*: ScConstruction.
*Returns*: ScAddr list of construction elements.

```py
    const = ScConstruction()
    const.create_node(sc_types.NODE_CONST, 'node')
    link_content = ScLinkContent("Hello!", ScLinkContentType.STRING.value)
    const.create_link(sc_types.LINK, link_content, 'link')
    const.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, 'node', 'link')
    addr_list = client.create_elements(const)
    addr_list # [node_addr, link_addr, edge_addr]
```


## delete_elements
Delete elements from KB memory.

*Parametrs*: list of ScAddr.
*Returns*: True if elements were deleted.

```py
status = client.delete_elements([node_addr, edge_addr, link_addr])
status #True
```

## set_link_contents
Set new content to given link.

*Parametrs*: list of ScLinkContent.
*Returns*: True if set link content.

```py
link_content = ScLinkContent("Hello world!", ScLinkContentType.STRING.value)
link_content.addr = link_addr
status = client.set_link_contents([link_content])
status # True
```

## get_link_content
Get content of given link.

*Parametrs*: ScAddr of link.
*Returns*: ScLinkContent object. 

```py
link_content = client.get_link_content(addr_list[0])
link_content.data # link content
link_content.addr # link addr
```

## get_link_by_content
Get link from KB by content.

*Parametrs*: List of ScLinkContent or list of string as link content, or .
*Returns*: List of lists of ScAddrs. 

```py
content = client.get_link_by_content(["testing search by link content as string", "no content"])
content[0] # get list of link ScAddrs with given content
content[1] # get empty list if no link with given content in memory
```

## resolve_keynodes
Get keynode from KB memory by idtf and ScType. If it doesn't exist, then create new one. If ScType is None, tries to find element by system identifier.

*Parametrs*: ScIdtfResolveParams.
*Returns*: ScAddr of keynode. 

```py
params = ScIdtfResolveParams(idtf='my_new_keynode_that_not_exist', type=sc_types.NODE_CONST)
addr = client.resolve_keynodes([params])
addr # new keynode addr

params = ScIdtfResolveParams(idtf='technology_OSTIS', type=sc_types.NODE_CONST)
addr = client.resolve_keynodes([params])
addr # keynode addr

params = ScIdtfResolveParams(idtf='my_another_keynode_that_not_exist', type=None)
addr = client.resolve_keynodes([params])
addr # None

params = ScIdtfResolveParams(idtf='nrel_format', type=None)
addr = client.resolve_keynodes([params])
addr # keynode addr
```


## template_search
Search in KB memory by template. 

*Parametrs*: ScTemplate or scs-temlate as string.
*Returns*: ScTemplateResult list. 

```py
templ = ScTemplate()
templ.triple([class_node_addr, '_class_node'], sc_types.EDGE_ACCESS_VAR_POS_PERM, node_addr) # faf
templ.triple('_class_node', sc_types.EDGE_ACCESS_VAR_POS_TEMP, link_addr) # faf
templ.triple('_class_node', edge_addr, sc_types.NODE_VAR) # ffa
templ.triple(node_addr, edge_addr, sc_types.NODE_VAR, is_required=False) # ffa, can be empty
search_results = client.template_search(templ)
search_result = search_results[0]

search_result.size() # count of elements in result construction
search_result.get(0).value # get element from result by index
search_result.get('_class_node').value # get element from result by alias

def for_each_tripple_func(src: ScAddr, edge: ScAddr, trg: ScAddr):
    ...
search_result.for_each_triple(for_each_tripple_func) # call function for each triple in result
```

## template_generate
Generate construction in KB memory by template.

*Parametrs*: ScTemplate or scs-temlate as string & ScTemplateGenParams.
*Returns*: ScTemplateResult object. 

```py
templ = ScTemplate()
templ.triple_with_relation( # faaaf
    [main_node, '_main_node'],
    sc_types.EDGE_D_COMMON_VAR,
    [sc_types.LINK, '_link'],
    sc_types.EDGE_ACCESS_VAR_POS_PERM,
    relation_node,
)
templ.triple( # faa
    '_main_node',
    sc_types.EDGE_ACCESS_VAR_POS_TEMP,
    [sc_types.NODE_VAR, '_var_node']
)
gen_params = {'_link': link_node, '_var_node': var_node}
gen_result = client.template_generate(templ, gen_params)
```


## events_create
Create an ScEvent in KB memory.

*Parametrs*: list of ScEventParams.
*Returns*: list of ScEvent. 

```py
def event_callback(src: ScAddr, edge: ScAddr, trg: ScAddr):
    ...

event_type = common.ScEventType.ADD_OUTGOING_EDGE
event_params = ScEventParams(bounded_elem_addr, event_type, event_callback)
sc_event = client.events_create([event_params])
```

## is_event_valid
Check is ScEvent active or not.

*Parametrs*: ScEvent.
*Returns*: True if event valid. 

```py
status = client.is_event_valid(sc_event)
status # True
```

## events_destroy
Destroy ScEvent in KB memory.

*Parametrs*: list of ScEvent.
*Returns*: True if event was destroyed. 

```py
status = client.events_destroy([sc_event])
status # true
```

# Classes

Python library contains python implementation of useful classes and functions to work with sc-memory.

There are a list of classes:

 - ScKeynodes
 - ScAgent
 - ScModule

## ScKeynodes
Singleton dictinary object which provide possibility to cache identifiers and addrs of keynodes stored in KB.
Create an instanse of ScKeynodes class to get access to cache:

```py
keynodes = ScKeynodes()
```

Get provided identifier:
```py
keynodes["identifier_of_keynode"] # returns ScAddr of given identifier
keynodes["not_stored_in_kb"] # returns invalid ScAddr if identifier does not exist in memory
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

## ScAgent
Class for handling single ScEvent. Define your agents like this:
```py
class MyAgent(ScAgent):
    action = "Identifier_of_action_class"
    
    def register(self) -> ScEvent:
        # override method, must return ScEvent instance
        params = [
            MyAgent.keynodes["action_initiated"],
            common.ScEventType.ADD_OUTGOING_EDGE,
            MyAgent.run_impl
        ]
        event_params = ScEventParams(*params)
        sc_event = client.events_create([event_params])
        return sc_event[0]
    
    @staticmethod
    def run_impl(action_class: ScAddr, edge: ScAddr, action_node: ScAddr) -> None:
        # override method, must have 3 args and be static
        ...

```

## ScModule
Class for handling multiple ScAgent. Define your modules like this:
```py 
class MyModule(ScModule):
    def __init__(self) -> None:
        agents_to_register = [MyAgent1, MyAgent2] # list of agent classes
        super().__init__(agents_to_register)
```
