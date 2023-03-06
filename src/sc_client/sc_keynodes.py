"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

import warnings
from enum import Enum
from typing import List, Optional

from sc_client import client
from sc_client.constants.sc_types import ScType
from sc_client.models import ScAddr, ScIdtfResolveParams


class ScKeynodes(dict):
    warnings.warn(
        "ScKeynodes moved to py-sc-kpm and will be removed from py-sc-client in version 0.3.0", DeprecationWarning
    )
    # TODO: remove class in version 0.3.0

    _instance = {}

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = dict.__new__(cls)
        return cls._instance

    def __getitem__(self, identifier: str, sc_type: Optional[ScType] = None) -> ScAddr:
        addr = self._instance.get(identifier)
        if addr is None:
            params = ScIdtfResolveParams(idtf=identifier, type=sc_type)
            addr = client.resolve_keynodes(params)[0]
            self._instance[identifier] = addr
        return addr

    def resolve_identifiers(self, identifiers: List[Enum]) -> None:
        idtf_list = [idtf_field.value for idtf_enum in identifiers for idtf_field in idtf_enum]
        params_list = (ScIdtfResolveParams(idtf=idtf, type=None) for idtf in idtf_list)
        addrs = client.resolve_keynodes(*params_list)
        self._instance.update(zip(idtf_list, addrs))
