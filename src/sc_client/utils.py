from __future__ import annotations

from typing import Dict

from sc_client.constants import common
from sc_client.constants.sc_types import ScType
from sc_client.models import ScTemplateValue, ScAddr


def process_triple_item(item: ScTemplateValue) -> Dict:
    item_value = item.get(common.VALUE)
    item_alias = item.get(common.ALIAS)
    if isinstance(item_value, ScAddr):
        result = {common.TYPE: common.Types.ADDR, common.VALUE: item_value.value}
    elif isinstance(item_value, ScType):
        result = {common.TYPE: common.Types.TYPE, common.VALUE: item_value.value}
    else:
        result = {common.TYPE: common.Types.ALIAS, common.VALUE: item_value}

    if item_alias:
        result[common.ALIAS] = item_alias
    return result
