import asyncio

from sc_client.core import AsyncScClient


async def main():
    client = AsyncScClient()
    await client.connect("ws://localhost:8090/ws_json")
    try:
        print(f"1. {client.is_connected()=}")
    finally:
        await client.disconnect()
        print(f"2. {client.is_connected()=}")


if __name__ == "__main__":
    asyncio.run(main())
