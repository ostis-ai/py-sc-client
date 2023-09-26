import asyncio

from sc_client.core import AScClient


async def main():
    client = AScClient()
    await client.connect("ws://localhost:8090/ws_json")
    try:
        print(f"1. {client.is_connected()=}")
    finally:
        await client.disconnect()
        print(f"2. {client.is_connected()=}")


if __name__ == "__main__":
    asyncio.run(main())
