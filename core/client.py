import asyncio
import logging
import argparse
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class ClientCore:
    def __init__(self, host="10.0.0.25", port=50000, alias="Anonymous"):
        self.host = host
        self.port = port
        self.alias = alias
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.receive_task: Optional[asyncio.Task] = None
        self.message_callback: Optional[Callable[[str], None]] = None
        self.connected = False

    def set_message_callback(self, callback: Callable[[str], None]):
        self.message_callback = callback

    async def connect(self) -> bool:
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            logger.info(f"Connected to server at {self.host}:{self.port}.")

            handshake_msg = f"__alias__:{self.alias}\n"
            self.writer.write(handshake_msg.encode())
            await self.writer.drain()

            self.connected = True
            self.receive_task = asyncio.create_task(self.receive_messages())
            return True
        except ConnectionRefusedError:
            logger.error(f"Connection to {self.host}:{self.port} refused.")
        except Exception as e:
            logger.error(f"Failed to connect to {self.host}:{self.port}: {e}")
        return False

    async def send_message(self, message: str):
        if not self.connected or not self.writer:
            return False

        try:
            self.writer.write(message.encode())
            await self.writer.drain()
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def receive_messages(self):
        while self.connected and not self.reader.at_eof():
            try:
                data = await self.reader.read(1024)
                if not data:
                    break

                message = data.decode().strip()
                if self.message_callback:
                    self.message_callback(message)
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                break

        self.connected = False

    def close(self):
        self.connected = False

        if self.receive_task:
            self.receive_task.cancel()

        if self.writer and not self.writer.is_closing():
            self.writer.close()

        logger.info("Connection closed.")


async def cli_mode(host: str, port: int, alias: str):
    def print_message(message: str):
        print(f">> {message}")

    client = ClientCore(host, port, alias)
    client.set_message_callback(print_message)

    if not await client.connect():
        print("Failed to connect to server.")
        return

    print(
        f"Connected as '{alias}'. Type messages and press Enter. Type 'quit' to exit."
    )

    try:
        while True:
            message = input()
            if message.lower() in ["quit", "exit"]:
                break
            await client.send_message(message)
    except KeyboardInterrupt:
        pass
    finally:
        client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network Chat Client")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Server host address (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port", type=int, default=50000, help="Server port (default: 50000)"
    )
    parser.add_argument(
        "--alias",
        type=str,
        default="Anonymous",
        help="Your chat alias (default: Anonymous)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    asyncio.run(cli_mode(args.host, args.port, args.alias))
