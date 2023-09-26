# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0]
### Added
 - Async usage (AScConnection and AScClient)
 - Opportunity to mock testing
### Changed
 - Object Oriented Programming style
 - Connection handlers
 - Exceptions
 - Models small features
   - Moved `ScType` to models directory
   - Made `value` field for `ScAddr` and `ScType` as property and cannot be changed in runtime
   - Add `__lt__` method for the ability to sort ScAddrs
 - Constants
 - Tests
 - Logging
 - Typing
### Removed
 - Storing of used sc-server responses
 - Deprecated usage of a list in `ScTemplate` triplets (now tuple and operator `>>`)
 - Deprecated methods of `ScTemplateResult`:
   - `results.size()`, use `len(results)`
   - `results.get(...)`, use `results[...]`
   - `results.for_each_triple(...)`, use `for src, edge, trd in results ...`
- `ScAgent`, `ScModule` and `ScKeynodes` (now in kpm)

## [0.3.0]
### Added
 - Reconnection retries to sc-server in messages sending
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
