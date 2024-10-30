# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Breaking changes
 - This version is compatible with version of the sc-machine 0.10.0. All API methods were redesigned. Incorrect ones were removed, new ones were added. See table below, to learn more about changes.
   
  | Deprecated method                       | Substitution method                        | 
  |-----------------------------------------|--------------------------------------------|
  | check_elements                          | get_elements_types                          |
  | create_elements                         | generate_elements                          |
  | create_node                             | generate_node                              |
  | create_link                             | generate_link                              |
  | create_edge                             | generate_connector                         |
  | create_elements_by_scs                  | generate_elements_by_scs                   | 
  | delete_elements                         | erase_elements                             |
  | get_links_by_contents                   | search_links_by_contentss                   |
  | get_links_by_content_substring          | search_links_by_contents_substrings         |
  | get_links_contents_by_content_substring | search_link_contents_by_content_substrings |
  | template_search                         | search_by_template                         |
  | template_generate                       | generate_by_template                       |
  | triple_with_relation                    | quintuple                                  |
  | events_create                           | create_elementary_event_subscriptions      |
  | events_destroy                          | destroy_elementary_event_subscriptions     |
  | is_event_valid                          | is_event_subscriptions_valid               |

 - `ScEvent` class was renamed to `ScEventSubscription`, `ScEventParams` class was renamed to `ScEventSubscriptionParams`, and sc-event types in `ScEventType` were changed according to the table below.

  | Removed sc-event type  | Substitution sc-event type  |
  |------------------------|-----------------------------|
  | ADD_OUTGOING_EDGE      | AFTER_GENERATE_OUTGOING_ARC |
  | ADD_INGOING_EDGE       | AFTER_GENERATE_INCOMING_ARC  |
  | REMOVE_OUTGOING_EDGE   | BEFORE_ERASE_OUTGOING_ARC   |
  | REMOVE_INGOING_EDGE    | BEFORE_ERASE_INCOMING_ARC    |
  | REMOVE_ELEMENT         | BEFORE_ERASE_ELEMENT        |
  | CONTENT_CHANGE         | BEFORE_CHANGE_LINK_CONTENT  |

  New sc-event types: `AFTER_GENERATE_CONNECTOR`, `AFTER_GENERATE_EDGE`, `BEFORE_ERASE_CONNECTOR`, `BEFORE_ERASE_EDGE` were added.

 - All sc-types were redesigned to a common style. They were deprecated, new ones were added. See changes in the table below.

  | Deprecated                          | Substitution                  |
  |-------------------------------------|-------------------------------|
  | sc_types.EDGE_U_COMMON              | sc_type.COMMON_EDGE           |
  | sc_types.EDGE_D_COMMON              | sc_type.COMMON_ARC            |
  | sc_types.EDGE_U_COMMON_CONST        | sc_type.CONST_COMMON_EDGE     |
  | sc_types.EDGE_D_COMMON_CONST        | sc_type.CONST_COMMON_ARC      |
  | sc_types.EDGE_ACCESS                | sc_type.MEMBERSHIP_ARC        |
  | sc_types.EDGE_ACCESS_CONST_POS_PERM | sc_type.CONST_PERM_POS_ARC    |
  | sc_types.EDGE_ACCESS_CONST_NEG_PERM | sc_type.CONST_PERM_NEG_ARC    |
  | sc_types.EDGE_ACCESS_CONST_FUZ_PERM | sc_type.CONST_FUZ_ARC         |
  | sc_types.EDGE_ACCESS_CONST_POS_TEMP | sc_type.CONST_TEMP_POS_ARC    |
  | sc_types.EDGE_ACCESS_CONST_NEG_TEMP | sc_type.CONST_TEMP_NEG_ARC    |
  | sc_types.EDGE_ACCESS_CONST_FUZ_TEMP | sc_type.CONST_FUZ_ARC         |
  | sc_types.EDGE_U_COMMON_VAR          | sc_type.VAR_COMMON_EDGE       |
  | sc_types.EDGE_D_COMMON_VAR          | sc_type.VAR_COMMON_ARC        |
  | sc_types.EDGE_ACCESS_VAR_POS_PERM   | sc_type.VAR_PERM_POS_ARC      |
  | sc_types.EDGE_ACCESS_VAR_NEG_PERM   | sc_type.VAR_PERM_NEG_ARC      |
  | sc_types.EDGE_ACCESS_VAR_FUZ_PERM   | sc_type.VAR_FUZ_ARC           |
  | sc_types.EDGE_ACCESS_VAR_POS_TEMP   | sc_type.VAR_TEMP_POS_ARC      |
  | sc_types.EDGE_ACCESS_VAR_NEG_TEMP   | sc_type.VAR_TEMP_NEG_ARC      |
  | sc_types.EDGE_ACCESS_VAR_FUZ_TEMP   | sc_type.VAR_FUZ_ARC           |
  | sc_types.NODE_CONST                 | sc_type.CONST_NODE            |
  | sc_types.NODE_VAR                   | sc_type.VAR_NODE              |
  | sc_types.LINK                       | sc_type.NODE_LINK             |
  | sc_types.LINK_CLASS                 | sc_type.NODE_LINK_CLASS       |
  | sc_types.NODE_STRUCT                | sc_type.NODE_STRUCTURE        |
  | sc_types.LINK_CONST                 | sc_type.CONST_NODE_LINK       |
  | sc_types.LINK_CONST_CLASS           | sc_type.CONST_NODE_LINK_CLASS |
  | sc_types.NODE_CONST_TUPLE           | sc_type.CONST_NODE_TUPLE      |
  | sc_types.NODE_CONST_STRUCT          | sc_type.CONST_NODE_STRUCTURE  |
  | sc_types.NODE_CONST_ROLE            | sc_type.CONST_NODE_ROLE       |
  | sc_types.NODE_CONST_NO_ROLE         | sc_type.CONST_NODE_NON_ROLE   |
  | sc_types.NODE_CONST_CLASS           | sc_type.CONST_NODE_CLASS      |
  | sc_types.NODE_CONST_MATERIAL        | sc_type.CONST_NODE_MATERIAL   |
  | sc_types.LINK_VAR                   | sc_type.VAR_NODE_LINK         |
  | sc_types.LINK_VAR_CLASS             | sc_type.VAR_NODE_LINK_CLASS   |
  | sc_types.NODE_VAR_STRUCT            | sc_type.VAR_NODE_STRUCTURE    |
  | sc_types.NODE_VAR_TUPLE             | sc_type.VAR_NODE_TUPLE        |
  | sc_types.NODE_VAR_ROLE              | sc_type.VAR_NODE_ROLE         |
  | sc_types.NODE_VAR_NO_ROLE           | sc_type.VAR_NODE_NON_ROLE      |
  | sc_types.NODE_VAR_CLASS             | sc_type.VAR_NODE_CLASS        |
  | sc_types.NODE_VAR_MATERIAL          | sc_type.VAR_NODE_MATERIAL     | 
  
- All sc-links are sc-nodes.
- Types of actual and inactual temporal membership sc-arc were added.
- Module `sc_types` is deprecated, use `sc_type` instead.
- Type `ScType.NodeAbstract` was removed.

### Added
 - ScType methods: `is_connector`, `is_structure`, `is_non_role`, `is_actual`, `is_inactual`, `is_superclass`
 - All possible combinations of subtypes into `sc-type` module
 - Type `sc_type.NODE_SUPERCLASS`
 - Types: `sc_type.CONNECTOR`, `sc_type.ARC`
 - Types of actual and inactual temporal sc-arcs
 - sc-event types: `AFTER_GENERATE_CONNECTOR`, `AFTER_GENERATE_OUTGOING_ARC`, `AFTER_GENERATE_INCOMING_ARC`, `AFTER_GENERATE_EDGE`, `BEFORE_ERASE_CONNECTOR`, `BEFORE_ERASE_OUTGOING_ARC`, `BEFORE_ERASE_INCOMING_ARC`,  `BEFORE_ERASE_EDGE`, `BEFORE_ERASE_ELEMENT`, `BEFORE_CHANGE_LINK_CONTENT`
 - ScClient methods: `get_elements_types`, `generate_elements`, `generate_node`, `generate_link`, `generate_connector`, `generate_elements_by_scs`, `erase_elements`, `search_links_by_contentss`, `search_links_by_contents_substrings`, `search_link_contents_by_content_substrings`, `search_by_template`, `generate_by_template`, `create_elementary_event_subscriptions`, `destroy_elementary_event_subscriptions`, `is_event_subscriptions_valid`
 - ScTemplate methods: `quintuple`

### Changed
 - `ScEvent` class was renamed to `ScEventSubscription`
 - `ScEventParams` class was renamed to `ScEventSubscriptionParams`

### Fixed
 - Checking of all syntactic and semantic subtypes for types in ScType `merge` method.
 - Now sc-link is sc-node

### Deprecated
 - ScType methods: `is_edge`, `is_struct`, `is_norole`
 - Module `sc_types`
 - sc-types: `sc_types.EDGE_U_COMMON`, `sc_types.EDGE_D_COMMON`, `sc_types.EDGE_U_COMMON_CONST`, `sc_types.EDGE_D_COMMON_CONST`, `sc_types.EDGE_ACCESS`, `sc_types.EDGE_ACCESS_CONST_POS_PERM`, `sc_types.EDGE_ACCESS_CONST_NEG_PERM`, `sc_types.EDGE_ACCESS_CONST_FUZ_PERM`, `sc_types.EDGE_ACCESS_CONST_POS_TEMP`, `sc_types.EDGE_ACCESS_CONST_NEG_TEMP`, `sc_types.EDGE_ACCESS_CONST_FUZ_TEMP`, `sc_types.EDGE_U_COMMON_VAR`, `sc_types.EDGE_D_COMMON_VAR`, `sc_types.EDGE_ACCESS_VAR_POS_PERM`, `sc_types.EDGE_ACCESS_VAR_NEG_PERM`, `sc_types.EDGE_ACCESS_VAR_FUZ_PERM`, `sc_types.EDGE_ACCESS_VAR_POS_TEMP`, `sc_types.EDGE_ACCESS_VAR_NEG_TEMP`, `sc_types.EDGE_ACCESS_VAR_FUZ_TEMP`, `sc_types.NODE_CONST`, `sc_types.NODE_VAR`, `sc_types.LINK`, `sc_types.LINK_CLASS`, `sc_types.NODE_STRUCT`, `sc_types.LINK_CONST`, `sc_types.LINK_CONST_CLASS`, `sc_types.NODE_CONST_TUPLE`, `sc_types.NODE_CONST_STRUCT`, `sc_types.NODE_CONST_ROLE`, `sc_types.NODE_CONST_NO_ROLE`, `sc_types.NODE_CONST_CLASS`, `sc_types.NODE_CONST_MATERIAL`, `sc_types.LINK_VAR`, `sc_types.LINK_VAR_CLASS`, `sc_types.NODE_VAR_STRUCT`, `sc_types.NODE_VAR_TUPLE`, `sc_types.NODE_VAR_ROLE`, `sc_types.NODE_VAR_NO_ROLE`, `sc_types.NODE_VAR_CLASS`, `sc_types.NODE_VAR_MATERIAL`
 - ScClient methods: `check_elements`, `create_elements`, `create_node`, `create_link`, `create_edge`, `create_elements_by_scs`, `delete_elements`, `get_links_by_contents`, `get_links_by_content_substring`, `get_links_contents_by_content_substring`, `template_search`, `template_generate`, `events_create`, `events_destroy`, `is_event_valid`
 - ScTemplate methods: `triple_with_relation`

### Removed
 - ScType method: `is_abstract`
 - sc-type `sc_types.NODE_ABSTRACT`
 - sc-event types: `ADD_OUTGOING_EDGE`, `ADD_INGOING_EDGE`, `REMOVE_OUTGOING_EDGE`, `REMOVE_INGOING_EDGE`, `REMOVE_ELEMENT`, `CONTENT_CHANGE`
 - Deprecated ScTemplateResult `size` method
 - Deprecated ScTemplateItem as list
 - Deprecated ScTemplateResult `for_each_triple` method
 - Deprecated `ScAgent` and `ScModule` classes

## [0.3.1]
### Fixed
- Undefined python interpreter version in CI
- Resolving keynodes with ScKeynodes class

## [0.3.0]
### Added
 - Reconnection retries to sc-server in send message
 - OnReconnect handler setter
 - OnError handler setter
### Fixed
 - Infinite loop when receiving response to message
### Removed
 - Reconnection to sc-server in separate thread by time

## [0.2.6]
### Added
 - Reconnection to sc-server can be enabled in connect params
### Changed
 - Decompose sc-types

## [0.2.5]
### Added
 - Output structure for generation by scs
 - Add autoreconnection to sc-server
 - Web-socket data size validation
### Changed
 - Change single logger to a logging hierarchy
 - Decompose models
 - Optimize ScTemplate, ScTemplateResult and change list to tuple in params
### Deprecated
 - ScModule, ScAgent and ScKeynode implementations moved to [py-sc-kpm](https://github.com/ostis-ai/py-sc-kpm)

## [0.2.4]
### Added
 - Find links contents by content substring
### Fixed
 - Fix error handling for single throw

## [0.2.3]
### Fixed
 - Change multiple loggers to a single with default configuration
 - Raise error if the server response return non-empty errors field
 - Raise error if the client API takes invalid argument

## [0.2.2]
### Fixed
 - Back compatibility with 0.2.0 version of the client

## [0.2.1]
### Added
 - Add opportunity to create elements by scs
 - Add tests for ScAddr and ScType classes
 - Add ScAddrEmpty class
### Changed
 - Change return type of ScTripleCallback to Enum
### Fixed
 - Raise error if the element will be passed with const type
### Removed
 - Removed method for checking direction of the edge

## [0.2.0]
### Added
 - Add opportunity to find links by substring
 - Add params for search
 - Add opportunity to pass template and params by addr and idtf
### Removed
 - Remove opportunity to not search some triples in sc-template, remove is_required flag,
   deprecated by [ostis-ai/sc-machine@49c5406](https://github.com/ostis-ai/sc-machine/commit/49c540646ba795ca2e6879ec3d3c2f1aa94f79ca)
### Changed
 - Specify link const types in tests and docs

## [0.1.2]
### Changed
 - README block of package installation

## [0.1.1]
### Changed
 - PyPi project to py-sc-client

## [0.1.0]
### Added
 - README and LICENSE files
 - Data classes of the sc-client for objects manipulating
 - API for connecting, disconnecting, and checking connection status with the sc-server
 - API for creating, and deleting elements in the sc-memory
 - API for checking the type of elements
 - API for setting and getting content of the sc-link
 - API for getting the list of sc-links by content
 - API for resolving sc-keynodes
 - API for generating and searching constructions in the sc-memory by template
 - API for sc-event registration and destroying in the sc-memory
 - API for checking the state of the sc-event
 - tests infrastructure for API
 - ScKeynodes class for caching identifiers and ScAddr objects
 - ScAgent class for handling a single ScEvent
 - ScModule class for handling a multiple ScAgent
 - Code linting tools: isort, pylint, black, pre-commit
 - Documentation for contributors and developers
 - CI for checking messages of commits
 - CI for code linting
 - CI for the testing package on multiple environments and python versions
 - CI for publishing package on PyPi
