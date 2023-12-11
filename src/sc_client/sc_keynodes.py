"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from enum import Enum
from typing import List

from sc_client import client
from sc_client.models import ScAddr, ScIdtfResolveParams


class ScKeynodes(dict):
    # TODO: remove class in version 0.3.0

    _instance = {}

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = dict.__new__(cls)
        return cls._instance

    def __getitem__(self, index) -> ScAddr:
        if isinstance(index, tuple) and len(index) == 2:
            identifier, sc_type = index
        else:
            identifier = index
            sc_type = None
        addr = self._instance.get(identifier)
        if addr is None or addr.value == 0:
            params = ScIdtfResolveParams(idtf=identifier, type=sc_type)
            addr = client.resolve_keynodes(params)[0]
            self._instance[identifier] = addr
        return addr

    def resolve_identifiers(self, identifiers: List[Enum]) -> None:
        idtf_list = [idtf_field.value for idtf_enum in identifiers for idtf_field in idtf_enum]
        params_list = (ScIdtfResolveParams(idtf=idtf, type=None) for idtf in idtf_list)
        addrs = client.resolve_keynodes(*params_list)
        self._instance.update(zip(idtf_list, addrs))
