"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from abc import ABC
from typing import List

from sc_client import client
from sc_client.sc_agent import ScAgent

_current_modules = []


class ScModule(ABC):
    def __init__(self, agents):
        if client.is_connected():
            self._agents = [agent() for agent in agents]
            _current_modules.append(self)
        else:
            raise RuntimeError("Cannot register agents: connection to the sc-server is not established")

    def _get_agents(self):
        return self._agents

    def _set_agents(self, value: List[ScAgent]):
        if not all(isinstance(agent, ScAgent) for agent in value):
            raise TypeError("All elements of the module agents list must be agents")
        self._agents = value

    agents = property(_get_agents, _set_agents)

    def unregister_agents(self) -> None:
        for agent in self.agents:
            agent.unregister()


def unregister_sc_modules():
    for module in _current_modules:
        module.unregister_agents()
    _current_modules.clear()
