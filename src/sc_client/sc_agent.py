"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from abc import ABC, abstractmethod

from sc_client import client
from sc_client.models import ScAddr, ScEvent
from sc_client.sc_keynodes import ScKeynodes


class ScAgent(ABC):
    keynodes = ScKeynodes()

    def __init__(self):
        self._event = self.register()

    def _get_event(self):
        return self._event

    def _set_event(self, event: ScEvent):
        if not isinstance(event, ScEvent):
            raise TypeError("An event must be an instance of ScEvent")
        self._event = event

    event = property(_get_event, _set_event)

    @abstractmethod
    def register(self) -> ScEvent:
        pass

    def unregister(self) -> None:
        client.events_destroy([self.event])

    @staticmethod
    @abstractmethod
    def run_impl(action_class: ScAddr, edge: ScAddr, action_node: ScAddr) -> None:
        pass
