import asyncio
import logging
import argparse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Server:
    def __init__(self, host="0.0.0.0", port=50000):
        self.host = host
        self.port = port
        self.server = None
        self.clients = set()

    async def broadcast(self, message: bytes, exclude: asyncio.StreamWriter = None):
        for w in self.clients:
            if w is not exclude:
                try:
                    w.write(message)
                    await w.drain()
                except Exception as e:
                    logger.error(
                        f"Error broadcasting to {w.get_extra_info('peername')}: {e}"
                    )
                    self.clients.discard(w)

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        client_addr = writer.get_extra_info("peername")
        handshake = await reader.readline()
        alias = handshake.decode().split(":", 1)[-1].strip()
        self.clients.add(writer)
        logger.info(f"New connection: {client_addr} as '{alias}'.")
        await self.broadcast(
            f"[+] {alias} has joined the chat!".encode(), exclude=writer
        )

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                logger.debug(
                    f"Received message from {alias}, {client_addr}: {data.decode()}."
                )
                await self.broadcast(
                    f"{alias}: {data.decode()}".encode(), exclude=writer
                )
        except Exception as e:
            logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            self.clients.discard(writer)
            writer.close()
            await writer.wait_closed()
            logger.info(f"Closed connection: {client_addr} as {alias}.")
            await self.broadcast(
                f"[-] {alias} has left the chat.".encode(), exclude=None
            )

    async def start(self):
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port,
        )
        logger.info(f"Server started on {self.host}:{self.port}.")
        async with self.server:
            await self.server.serve_forever()

    def stop(self):
        logger.info("Stopping server...")
        if self.server:
            self.server.close()


if __name__ == "__main__":
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
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        server.stop()
        logger.info("Server stopped gracefully.")