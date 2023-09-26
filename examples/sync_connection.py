from sc_client.core import ScClient


def main():
    client = ScClient()
    client.connect("ws://localhost:8090/ws_json")
    try:
        print(f"1. {client.is_connected()=}")
    finally:
        client.disconnect()
        print(f"2. {client.is_connected()=}")


if __name__ == "__main__":
    main()
