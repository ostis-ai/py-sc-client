import logging

from sc_client.core import ScClient

logging.basicConfig(level=logging.DEBUG)


def on_open():
    logging.info("Callback on open")


def on_close():
    logging.info("Callback on close")


def main():
    client = ScClient()
    client.set_on_open_handler(on_open)
    client.set_on_close_handler(on_close)
    client.connect("ws://localhost:8090/ws_json")  # INFO:root:Callback on open
    try:
        ...
    finally:
        client.disconnect()  # INFO:root:Callback on close


if __name__ == "__main__":
    main()
