import asyncio
import logging
import signal
import ssl

from typing import List
from .protocol.io import write_message, read_message

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Server:
    def __init__(self, host="0.0.0.0", port=50000, tls=False):
        self.host = host
        self.port = port
        self.tls = tls
        self.server = None
        self.writers = set()

    async def close_writer(self, writer: asyncio.StreamWriter):
        self.writers.discard(writer)
        writer.close()
        await writer.wait_closed()

    async def broadcast(self, message: str, exclude: List[asyncio.StreamWriter] = []):
        message = message.encode()
        writers = self.writers.difference(exclude)
        for writer in writers:
            try:
                await write_message(writer, message)
            except ConnectionError as e:
                logger.error(
                    f"Error broadcasting to {writer.get_extra_info('peername')}: {e}"
                )
                await self.close_writer(writer)

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        client_addr = writer.get_extra_info("peername")
        handshake = await read_message(reader)
        alias = handshake.split(":", 1)[-1].strip()
        self.writers.add(writer)
        logger.info(f"[+] New connection: {client_addr} as '{alias}'.")
        await self.broadcast(f"[+] {alias} has joined the chat!", exclude=[writer])
        try:
            while True:
                message = await read_message(reader)
                logger.debug(
                    f"Received message from {alias}, {client_addr}: {message}."
                )
                await self.broadcast(f"{alias}: {message}", exclude=[writer])
        # TODO: Error handling for client disconnection
        finally:
            await self.close_writer(writer)
            logger.info(f"[-] Closed connection: {client_addr} as {alias}.")
            await self.broadcast(f"[-] {alias} has left the chat.")

    async def start(self):
        ssl_context = None
        if self.tls:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain("ssl/server.crt", "ssl/server.key")
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port,
            ssl=ssl_context,
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

    async def run(self):
        try:
            await self.start()
        except asyncio.CancelledError:
            await self.stop()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Async TCP Server")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host address to bind the server (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=50000,
        help="Port to bind the server (default: 50000)",
    )
    parser.add_argument("--tls", action="store_true", help="Enable TLS")
    args = parser.parse_args()
    server = Server(host=args.host, port=args.port, tls=args.tls)

    # https://stackoverflow.com/questions/48562893/how-to-gracefully-terminate-an-asyncio-script-with-ctrl-c
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_task = asyncio.ensure_future(server.run())
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()


if __name__ == "__main__":
    main()
