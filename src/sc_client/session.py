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
from typing import Any, Callable

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


def default_error_handler(error: Exception) -> None:
    raise error


class _ScClientSession:
    is_open = False
    lock_instance = threading.Lock()
    responses_dict = {}
    events_dict = {}
    command_id = 0
    executor = Executor()
    ws_app: websocket.WebSocketApp | None = None
    error_handler: Callable[[Exception], None] = default_error_handler
    reconnect_callback: Callable[[], None] = default_reconnect_handler
    post_reconnect_callback: Callable[[], None] = lambda *args: None
    reconnect_retries: int = SERVER_RECONNECT_RETRIES
    reconnect_retry_delay: float = SERVER_RECONNECT_RETRY_DELAY
    last_healthcheck_answer: str = None

    @classmethod
    def clear(cls):
        cls.is_open = False
        cls.responses_dict = {}
        cls.events_dict = {}
        cls.command_id = 0
        cls.ws_app = None
        cls.error_handler = default_error_handler
        cls.reconnect_callback = default_reconnect_handler
        cls.post_reconnect_callback = lambda *args: None
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
    logger.info("New connection opened")
    _ScClientSession.is_open = True


def _on_error(_, error: Exception) -> None:
    _ScClientSession.error_handler(error)


def _on_close(_, _close_status_code, _close_msg) -> None:
    logger.info("Connection closed")
    _ScClientSession.is_open = False


def set_error_handler(callback) -> None:
    _ScClientSession.error_handler = callback


def set_reconnect_handler(
    reconnect_callback, post_reconnect_callback, reconnect_retries: int, reconnect_retry_delay: float
) -> None:
    _ScClientSession.reconnect_callback = reconnect_callback
    _ScClientSession.post_reconnect_callback = post_reconnect_callback
    _ScClientSession.reconnect_retries = reconnect_retries
    _ScClientSession.reconnect_retry_delay = reconnect_retry_delay


def set_connection(url: str) -> None:
    establish_connection(url)


def is_connected() -> bool:
    return _ScClientSession.is_open


def establish_connection(url) -> None:
    def run_in_thread():
        _ScClientSession.ws_app = websocket.WebSocketApp(
            url,
            on_open=_on_open,
            on_message=_on_message,
            on_error=_on_error,
            on_close=_on_close,
        )
        logger.info(f"Sc-server socket: {_ScClientSession.ws_app.url}")
        try:
            _ScClientSession.ws_app.run_forever()
        except websocket.WebSocketException as e:
            _on_error(_ScClientSession.ws_app, e)

    client_thread = threading.Thread(target=run_in_thread, name="sc-client-session-thread")
    client_thread.start()
    time.sleep(SERVER_ESTABLISH_CONNECTION_TIME)

    if _ScClientSession.is_open:
        _ScClientSession.post_reconnect_callback()


def close_connection() -> None:
    try:
        _ScClientSession.ws_app.close()
        _ScClientSession.is_open = False
    except AttributeError as e:
        _on_error(_ScClientSession.ws_app, e)


def receive_message(command_id: int) -> Response:
    response = None
    while not response and _ScClientSession.is_open:
        response = _ScClientSession.responses_dict.get(command_id)
        time.sleep(SERVER_ANSWER_CHECK_TIME)
    return response


def _send_message(data: str, retries: int, retry: int = 0) -> None:
    try:
        logger.debug(f"Send: {data[:LOGGING_MAX_SIZE]}")
        _ScClientSession.ws_app.send(data)
    except websocket.WebSocketConnectionClosedException:
        if _ScClientSession.reconnect_callback and retry < retries:
            logger.warning(
                f"Connection to sc-server has failed. "
                f"Trying to reconnect to sc-server socket in {_ScClientSession.reconnect_retry_delay} seconds"
            )
            if retry > 0:
                time.sleep(_ScClientSession.reconnect_retry_delay)
            _ScClientSession.reconnect_callback()
            _send_message(data, retries, retry + 1)
        else:
            _on_error(_ScClientSession.ws_app, ConnectionAbortedError("Sc-server takes a long time to respond"))


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
        _on_error(
            _ScClientSession.ws_app, PayloadMaxSizeError(f"Data is too large: {len_data} > {MAX_PAYLOAD_SIZE} bytes")
        )

    def _handle_message() -> Response:
        _send_message(data, _ScClientSession.reconnect_retries)
        return receive_message(command_id)

    response = _handle_message()
    if not response:
        _on_error(_ScClientSession.ws_app, ConnectionAbortedError("Sc-server takes a long time to respond"))

    return response


def get_event(event_id: int) -> ScEvent | None:
    return _ScClientSession.events_dict.get(event_id)


def drop_event(event_id: int):
    del _ScClientSession.events_dict[event_id]


def set_event(sc_event: ScEvent) -> None:
    _ScClientSession.events_dict[sc_event.id] = sc_event


def execute(request_type: ClientCommand, *args):
    return _ScClientSession.executor.run(request_type, *args)
