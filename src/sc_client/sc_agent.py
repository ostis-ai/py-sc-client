"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

import warnings
from abc import ABC, abstractmethod

from sc_client import client
from sc_client.models import ScAddr, ScEvent
from sc_client.sc_keynodes import ScKeynodes


class ScAgent(ABC):
    warnings.warn(
        "ScAgent moved to py-sc-kpm and will be removed from py-sc-client in version 0.3.0", DeprecationWarning
    )
    # TODO: remove class in version 0.3.0

    keynodes = ScKeynodes()

    def __init__(self):
        self._event = self.register()

    @property
    def event(self) -> ScEvent:
        return self._event

    @event.setter
    def event(self, event: ScEvent) -> None:
        if not isinstance(event, ScEvent):
            raise TypeError("An event must be an instance of ScEvent")
        self._event = event

    @abstractmethod
    def register(self) -> ScEvent:
        pass

    def unregister(self) -> None:
        client.events_destroy(self._event)

    @staticmethod
    @abstractmethod
    def run_impl(action_class: ScAddr, edge: ScAddr, action_node: ScAddr) -> None:
        pass
