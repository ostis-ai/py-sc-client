"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any

import websocket

from sc_client.client._executor import Executor
from sc_client.constants import common
from sc_client.constants.common import ClientCommand
from sc_client.constants.exceptions import PayloadMaxSizeError
from sc_client.constants.numeric import (
    LOGGING_MAX_SIZE,
    MAX_PAYLOAD_SIZE,
    SERVER_ANSWER_CHECK_TIME,
    SERVER_ESTABLISH_CONNECTION_TIME,
    SERVER_RECONNECT_RETRIES,
    SERVER_RECONNECT_RETRY_DELAY,
)
from sc_client.models import Response, ScAddr, ScEvent

logger = logging.getLogger(__name__)


def default_reconnect_handler() -> None:
    establish_connection(_ScClientSession.ws_app.url)


class _ScClientSession:
    is_open = False
    lock_instance = threading.Lock()
    responses_dict = {}
    events_dict = {}
    command_id = 0
    executor = Executor()
    ws_app: websocket.WebSocketApp | None = None
    error_handler = None
    reconnect_callback = default_reconnect_handler
    post_reconnect_callback = None
    reconnect_retries: int = SERVER_RECONNECT_RETRIES
    reconnect_retry_delay: float = SERVER_RECONNECT_RETRY_DELAY

    @classmethod
    def clear(cls):
        cls.is_open = False
        cls.responses_dict = {}
        cls.events_dict = {}
        cls.command_id = 0
        cls.ws_app = None
        cls.error_handler = None
        cls.reconnect_callback = default_reconnect_handler
        cls.post_reconnect_callback = None
        cls.reconnect_retries = SERVER_RECONNECT_RETRIES
        cls.reconnect_retry_delay = SERVER_RECONNECT_RETRY_DELAY


def _on_message(_, response: str) -> None:
    logger.debug(f"Receive: {str(response)[:LOGGING_MAX_SIZE]}")
    response = json.loads(response, object_hook=Response)
    if response.get(common.EVENT):
        threading.Thread(
            target=_emit_callback,
            args=(response.get(common.ID), response.get(common.PAYLOAD)),
        ).start()
    else:
        _ScClientSession.responses_dict[response.get(common.ID)] = response


def _emit_callback(event_id: int, elems: list[int]) -> None:
    event = _ScClientSession.events_dict.get(event_id)
    if event:
        event.callback(*[ScAddr(addr) for addr in elems])


def _on_open(_) -> None:
    _ScClientSession.is_open = True


def _on_error(_, error: Exception) -> None:
    if _ScClientSession.error_handler:
        _ScClientSession.error_handler(error)
    else:
        raise error


def _on_close(_, close_status_code, close_msg) -> None:
    close_connection()
    _ScClientSession.is_open = False
    if close_status_code and close_msg:
        logger.info(f"{close_status_code}: {close_msg}")


def set_error_handler(callback) -> None:
    _ScClientSession.error_handler = callback


def set_reconnect_handler(
        reconnect_callback, post_reconnect_callback, reconnect_retries: int, reconnect_retry_delay: float) -> None:
    _ScClientSession.reconnect_callback = reconnect_callback
    _ScClientSession.post_reconnect_callback = post_reconnect_callback
    _ScClientSession.reconnect_retries = reconnect_retries
    _ScClientSession.reconnect_retry_delay = reconnect_retry_delay


def set_connection(url: str) -> None:
    establish_connection(url)


def establish_connection(url) -> None:
    def run_in_thread():
        if not _ScClientSession.ws_app or _ScClientSession.ws_app.url != url:
            _ScClientSession.ws_app = websocket.WebSocketApp(
                url,
                on_message=_on_message,
                on_error=_on_error,
                on_close=_on_close,
            )
            logger.info(f"Sc-server socket: {_ScClientSession.ws_app.url}")
        if not _ScClientSession.is_open:
            try:
                _ScClientSession.ws_app.run_forever()
            except websocket.WebSocketException as e:
                _on_error(None, e)

    client_thread = threading.Thread(target=run_in_thread, name="sc-client-session-thread")
    client_thread.start()
    logger.info(f"Trying to establish connection to socket")
    time.sleep(SERVER_ESTABLISH_CONNECTION_TIME)


def close_connection() -> None:
    try:
        _ScClientSession.ws_app.close()
    except AttributeError as e:
        _on_error(None, e)
    logger.debug("Disconnected")


def receive_message(command_id: int) -> Response:
    response = None
    while not response:
        response = _ScClientSession.responses_dict.get(command_id)
        time.sleep(SERVER_ANSWER_CHECK_TIME)
    return response


def _send_message(data: str, retries: int, retry_delay: float, retry: int = 0) -> None:
    try:
        logger.debug(f"Send: {data[:LOGGING_MAX_SIZE]}")
        _ScClientSession.ws_app.send(data)
    except websocket.WebSocketException as e:
        close_connection()
        if _ScClientSession.reconnect_callback and retry < retries:
            logger.warning(f"Connection to sc-server has failed. Trying to reconnect to sc-server socket")
            time.sleep(retry_delay)
            _ScClientSession.reconnect_callback()
            if _ScClientSession.post_reconnect_callback:
                _ScClientSession.post_reconnect_callback()
            _send_message(data, retries, retry_delay, retry + 1)
        else:
            _on_error(None, e)


def send_message(request_type: common.ClientCommand, payload: Any) -> Response:
    with _ScClientSession.lock_instance:
        _ScClientSession.command_id += 1
        command_id = _ScClientSession.command_id
    data = json.dumps(
        {
            common.ID: command_id,
            common.TYPE: request_type.value,
            common.PAYLOAD: payload,
        }
    )
    len_data = len(bytes(data, "utf-8"))
    if len_data > MAX_PAYLOAD_SIZE:
        _on_error(None, PayloadMaxSizeError(f"Data is too large: {len_data} > {MAX_PAYLOAD_SIZE} bytes"))
    _send_message(data, _ScClientSession.reconnect_retries, _ScClientSession.reconnect_retry_delay)
    response = receive_message(command_id)
    return response


def get_event(event_id: int) -> ScEvent | None:
    return _ScClientSession.events_dict.get(event_id)


def drop_event(event_id: int):
    del _ScClientSession.events_dict[event_id]


def set_event(sc_event: ScEvent) -> None:
    _ScClientSession.events_dict[sc_event.id] = sc_event


def execute(request_type: ClientCommand, *args):
    return _ScClientSession.executor.run(request_type, *args)
