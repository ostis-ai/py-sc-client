from dataclasses import dataclass
from typing import List, Union

from sc_client.models import ScAddr


@dataclass
class SCs:
    text: str
    output_struct: ScAddr = ScAddr(0)


SCsText = List[Union[str, SCs]]
