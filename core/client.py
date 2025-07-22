import asyncio
import logging
import struct
import signal
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
            # Length-prefix the message for easier server-side parsing
            message_bytes = message.encode()
            length = len(message_bytes)
            self.writer.write(struct.pack("!I", length))
            self.writer.write(message_bytes)
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

    async def close(self):
        self.connected = False

        if self.receive_task:
            self.receive_task.cancel()

        if self.writer and not self.writer.is_closing():
            self.writer.close()
            await self.writer.wait_closed()

        logger.info("Connection closed.")


async def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Async TCP Client")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Server host address (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=50000,
        help="Server port (default: 50000)",
    )
    parser.add_argument(
        "--alias",
        type=str,
        default="Anonymous",
        help="Client alias (default: Anonymous)",
    )
    args = parser.parse_args()

    client = ClientCore(host=args.host, port=args.port, alias=args.alias)

    def signal_handler():
        logger.info("Received interrupt signal")
        asyncio.create_task(client.close())
        sys.exit(0)

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)

    client.set_message_callback(lambda msg: print(f"Received: {msg}"))

    if not await client.connect():
        logger.error("Failed to connect to server")
        return

    try:
        while client.connected:
            message = await asyncio.to_thread(input, "Enter message: ")
            if message.lower() in ["quit", "exit"]:
                break
            await client.send_message(message)
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
