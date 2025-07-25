import asyncio
import logging
import struct
import signal

from typing import List
from utils.io import read_message, ConnectionCloseError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

MAX_MESSAGE_LENGTH = 1024  # Maximum length of a message in bytes


class Server:
    def __init__(self, host="0.0.0.0", port=50000):
        self.host = host
        self.port = port
        self.server = None
        self.clients = set()

    async def broadcast(self, message: str, exclude: List[asyncio.StreamWriter] = []):
        message = message.encode()
        for writer in self.clients:
            if writer not in exclude:
                try:
                    writer.write(struct.pack("!I", len(message)))  # Send length first
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
        handshake = await read_message(reader)
        alias = handshake.split(":", 1)[-1].strip()
        self.clients.add(writer)
        logger.info(f"[+] New connection: {client_addr} as '{alias}'.")
        await self.broadcast(f"[+] {alias} has joined the chat!", exclude=[writer])
        try:
            while True:
                message = await read_message(reader)
                logger.debug(
                    f"Received message from {alias}, {client_addr}: {message}."
                )
                await self.broadcast(f"{alias}: {message}", exclude=[writer])
        # TODO: Better error handling and reconnection logic
        except ConnectionCloseError:
            pass
        finally:
            self.clients.discard(writer)
            writer.close()
            await writer.wait_closed()
            logger.info(f"[-] Closed connection: {client_addr} as {alias}.")
            await self.broadcast(f"[-] {alias} has left the chat.")

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
            self.server.close_clients()
            await self.server.wait_closed()
        logger.info("Server stopped gracefully.")


async def main_coro():
    try:
        await server.start()
    except asyncio.CancelledError:
        await server.stop()


if __name__ == "__main__":
    import argparse

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

    # https://stackoverflow.com/questions/48562893/how-to-gracefully-terminate-an-asyncio-script-with-ctrl-c
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_task = asyncio.ensure_future(main_coro())
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()
