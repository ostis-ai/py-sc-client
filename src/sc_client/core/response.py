from __future__ import annotations

import json
from dataclasses import dataclass

from sc_client.constants import common


@dataclass
class Response:
    id: int
    status: bool
    event: bool
    payload: any
    errors: any

    @classmethod
    def load(cls, response: str) -> Response:
        response: dict[str, any] = json.loads(response)
        instance = cls(
            id=response.get(common.ID),
            status=bool(response.get(common.STATUS)),
            event=bool(response.get(common.EVENT)),
            payload=response.get(common.PAYLOAD),
            errors=response.get(common.ERRORS),
        )
        return instance

    def dump(self) -> str:
        return json.dumps(
            {
                common.ID: self.id,
                common.STATUS: int(self.status),
                common.EVENT: int(self.event),
                common.PAYLOAD: self.payload,
                common.ERRORS: self.errors,
            }
        )
