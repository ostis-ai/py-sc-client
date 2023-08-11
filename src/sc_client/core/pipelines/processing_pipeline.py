from __future__ import annotations

import abc
import logging

from sc_client.constants.common import MESSAGE, REF, ClientCommand, RequestType
from sc_client.core.sc_connection import ScConnection
from sc_client.models import Response
from sc_client.sc_exceptions import ScServerError


class ProcessingPipeline(abc.ABC):
    command_type: ClientCommand
    request_type: RequestType

    def __init__(self, sc_connection: ScConnection) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._sc_connection = sc_connection

    def _process_errors(self, response: Response, payload: any) -> None:
        errors = response.errors
        if errors:
            error_msgs = []
            if isinstance(errors, str):
                error_msgs.append(errors)
            else:
                for error in errors:
                    payload_part = f"\nPayload: {payload[int(error.get(REF))]}" if error.get(REF) else ""
                    error_msgs.append(error.get(MESSAGE) + payload_part)
            error_msgs = "\n".join(error_msgs)
            error = ScServerError(error_msgs)
            self._logger.error(error, exc_info=True)
            raise error
