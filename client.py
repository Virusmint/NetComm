import asyncio
import logging
import argparse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Client:
    def __init__(self, host="10.0.0.25", port=50000, alias="Anonymous"):
        self.host = host
        self.port = port
        self.alias = alias
        self.reader: asyncio.StreamReader = None
        self.writer: asyncio.StreamWriter = None
        self.send_task: asyncio.Task = None
        self.receive_task: asyncio.Task = None

    async def connect(self) -> bool:
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            logger.info(f"Connected to server at {self.host}:{self.port}.")
            # Send handshake message with alias
            handshake_msg = f"__alias__:{self.alias}\n"
            self.writer.write(handshake_msg.encode())
            await self.writer.drain()
            return True
        except ConnectionRefusedError:
            logger.error(f"Connection to {self.host}:{self.port} refused.")
        except Exception as e:
            logger.error(f"Failed to connect to {self.host}:{self.port}: {e}")
        return False

    async def run(self):
        if not await self.connect():
            logger.error("Could not establish connection. Exiting.")
            return
        self.send_task = asyncio.create_task(self.send_messages())
        self.receive_task = asyncio.create_task(self.receive_messages())
        done, pending = await asyncio.wait(
            [self.send_task, self.receive_task],
            return_when=asyncio.FIRST_COMPLETED,  # Wait for either async task to complete
        )
        for task in pending:
            logger.debug(f"Cancelling pending task: {task}")
            task.cancel()  # Cancel the other pending task
        self.close()

    async def send_messages(self):
        while True:
            msg = await asyncio.to_thread(input, "> ")
            if msg.lower() in {"exit", "quit"}:
                logger.info("Exiting...")
                break
            self.writer.write(msg.encode())
            await self.writer.drain()

    async def receive_messages(self):
        while not self.reader.at_eof():
            data = await self.reader.read(1024)
            if not data:
                break
            print(f"\r{data.decode()}\n> ", end="", flush=True)

    def close(self):
        if self.send_task:
            self.send_task.cancel()
        if self.receive_task:
            self.receive_task.cancel()
        if self.writer and not self.writer.is_closing():
            self.writer.close()
        logger.info("Connection closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Async TCP Chat Client")
    parser.add_argument(
        "--host", type=str, default="10.0.0.25", help="Server host (default: 10.0.0.25)"
    )
    parser.add_argument(
        "--port", type=int, default=50000, help="Server port (default: 50000)"
    )
    parser.add_argument(
        "--name", default="Anonymous", help="Alias/Nickname to use in chat"
    )
    args = parser.parse_args()
    client = Client(host=args.host, port=args.port, alias=args.name)
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        client.close()
        logger.info("Client application terminated by user (KeyboardInterrupt).")
