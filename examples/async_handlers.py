import asyncio
import logging

from sc_client.core import AScClient

logging.basicConfig(level=logging.INFO)


async def on_open():
    logging.info("Callback on open")


async def on_close():
    logging.info("Callback on close")


async def main():
    client = AScClient()
    client.set_on_open_handler(on_open)
    client.set_on_close_handler(on_close)
    await client.connect("ws://localhost:8090/ws_json")  # INFO:root:Callback on open
    try:
        ...
    finally:
        await client.disconnect()  # INFO:root:Callback on close


if __name__ == "__main__":
    asyncio.run(main())
