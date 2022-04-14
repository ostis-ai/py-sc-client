from __future__ import annotations

import json
import threading
import time
from typing import Any, List, Optional

import websocket

from log import get_default_logger
from sc_client.constants import common
from sc_client.constants.numeric import LOGGING_MAX_SIZE, SERVER_ESTABLISH_CONNECTION_TIME, SERVER_ANSWER_CHECK_TIME
from sc_client.models import Response, ScAddr, ScEvent

logger = get_default_logger(__name__)


class _ScClientSession:
    lock_instance = threading.Lock()
    responses_dict = {}
    events_dict = {}
    command_id = 0
    ws_app = None

    @classmethod
    def clear(cls):
        cls.responses_dict = {}
        cls.events_dict = {}
        cls.command_id = 0
        cls.ws_app = None


def _on_message(_, response: str) -> None:
    logger.debug(f"Receive: {str(response)[:LOGGING_MAX_SIZE]}")
    response = json.loads(response, object_hook=Response)
    if response.get(common.EVENT):
        threading.Thread(target=_emit_callback, args=(response.get(common.ID), response.get(common.PAYLOAD))).start()
    else:
        _ScClientSession.responses_dict[response.get(common.ID)] = response


def _emit_callback(event_id: int, elems: List[int]) -> None:
    event = _ScClientSession.events_dict.get(event_id)
    if event:
        event.callback(*[ScAddr(addr) for addr in elems])


def _on_error(_, error: Exception) -> None:
    close_connection()
    logger.error(f"{error}. Close connection")


def _on_close(_, close_status_code, close_msg) -> None:
    close_connection()
    logger.info(f"{close_status_code}: {close_msg}")


def is_connection_established() -> bool:
    return bool(_ScClientSession.ws_app)


def set_connection(url: str) -> None:
    if not is_connection_established():
        establish_connection(url)
    if not is_connection_established():
        raise ConnectionRefusedError


def establish_connection(url) -> None:
    def run_in_thread(url_for_ws_app: str):
        _ScClientSession.ws_app = websocket.WebSocketApp(
            url_for_ws_app,
            on_message=_on_message,
            on_error=_on_error,
            on_close=_on_close,
        )
        _ScClientSession.ws_app.run_forever()

    client_thread = threading.Thread(target=run_in_thread, args=(url,), name="sc-client-session-thread")
    client_thread.start()
    logger.debug("Connected")
    time.sleep(SERVER_ESTABLISH_CONNECTION_TIME)


def close_connection() -> None:
    _ScClientSession.ws_app.close()
    _ScClientSession.ws_app = None
    logger.debug("Disconnected")


def receive_message(command_id: int) -> Response:
    response = None
    while not response:
        response = _ScClientSession.responses_dict.get(command_id)
        time.sleep(SERVER_ANSWER_CHECK_TIME)
    return response


def send_message(request_type: str, payload: Any) -> Response:
    if not is_connection_established():
        raise BrokenPipeError
    with _ScClientSession.lock_instance:
        _ScClientSession.command_id += 1
        command_id = _ScClientSession.command_id
    data = json.dumps({
        common.ID: command_id,
        common.TYPE: request_type,
        common.PAYLOAD: payload
    })
    _ScClientSession.ws_app.send(data)
    logger.debug(f"Send: {data[:LOGGING_MAX_SIZE]}")
    response = receive_message(command_id)
    return response


def get_event(event_id: int) -> Optional[ScEvent]:
    return _ScClientSession.events_dict.get(event_id)


def drop_event(event_id: int):
    del _ScClientSession.events_dict[event_id]


def set_event(sc_event: ScEvent) -> None:
    _ScClientSession.events_dict[sc_event.id] = sc_event
