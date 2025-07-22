import asyncio
import logging
import argparse
import struct
import sys
import signal
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

MAX_MESSAGE_LENGTH = 1024  # Maximum length of a message in bytes


class Server:
    def __init__(self, host="0.0.0.0", port=50000):
        self.host = host
        self.port = port
        self.server = None
        self.clients = set()

    async def broadcast(self, message: bytes, exclude: List[asyncio.StreamWriter] = []):
        for writer in self.clients:
            if writer not in exclude:
                try:
                    writer.write(message)
                    await writer.drain()
                except Exception as e:
                    logger.error(
                        f"Error broadcasting to {writer.get_extra_info('peername')}: {e}"
                    )
                    self.clients.discard(writer)

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        client_addr = writer.get_extra_info("peername")
        handshake = await reader.readline()
        alias = handshake.decode().split(":", 1)[-1].strip()
        self.clients.add(writer)
        logger.info(f"[+] New connection: {client_addr} as '{alias}'.")
        await self.broadcast(
            f"[+] {alias} has joined the chat!".encode(), exclude=[writer]
        )

        try:
            while True:
                length_bytes = await reader.readexactly(4)
                if not length_bytes:
                    break
                length = struct.unpack("!I", length_bytes)[0]
                data = await reader.readexactly(length)
                message = data.decode()
                logger.debug(
                    f"Received message from {alias}, {client_addr}: {message}."
                )
                await self.broadcast(f"{alias}: {message}".encode(), exclude=[writer])
        except Exception as e:
            logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            self.clients.discard(writer)
            writer.close()
            await writer.wait_closed()
            logger.info(f"[-] Closed connection: {client_addr} as {alias}.")
            await self.broadcast(f"[-] {alias} has left the chat.".encode())

    async def start(self):
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port,
        )
        logger.info(f"Server started on {self.host}:{self.port}.")
        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        logger.info("Stopping server...")
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        for writer in list(self.clients):
            writer.close()
            await writer.wait_closed()
        self.clients.clear()
        logger.info("Server stopped gracefully.")


async def main():
    parser = argparse.ArgumentParser(description="Async TCP Server")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind the server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=50000,
        help="Port to bind the server (default: 50000)",
    )
    args = parser.parse_args()

    server = Server(host=args.host, port=args.port)

    def signal_handler():
        logger.info("Received interrupt signal")
        asyncio.create_task(server.stop())

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)

    try:
        await server.start()
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
