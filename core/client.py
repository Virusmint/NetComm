import asyncio
import logging
import signal
import sys
from typing import Optional, Callable, Literal

from utils.io import write_message, read_message, ConnectionCloseError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Client:
    def __init__(self, host="10.0.0.25", port=50000, alias="Anonymous"):
        self.host = host
        self.port = port
        self.alias = alias
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.send_task: Optional[asyncio.Task] = None
        self.receive_task: Optional[asyncio.Task] = None
        self.message_callback: Optional[Callable[[str], None]] = None

    def set_message_callback(self, callback: Callable[[str], None]):
        self.message_callback = callback

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        await self.send_message(f"__alias__:{self.alias}")

    async def send_message(self, message: str):
        await write_message(self.writer, message)

    async def receive_messages(self):
        while True:
            try:
                message = await read_message(self.reader)
                if self.message_callback:
                    self.message_callback(message)
            except asyncio.CancelledError:
                break

    async def send_messages_cli(self):
        stdin_reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(stdin_reader)
        loop = asyncio.get_event_loop()
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        print("> ", end="", flush=True)
        while True:
            try:
                line = await stdin_reader.readline()
                if not line:  # EOF
                    break
                message = line.decode().strip()
                if message.lower() in ("exit", "quit"):
                    await self.stop()
                await self.send_message(message)
                print("> ", end="", flush=True)
            except asyncio.CancelledError:
                break

    async def start(self, mode: Literal["cli", "gui"]):
        await self.connect()
        if mode == "cli":
            self.receive_task = asyncio.create_task(self.receive_messages())
            self.send_task = asyncio.create_task(self.send_messages_cli())
            await asyncio.gather(
                self.receive_task, self.send_task, return_exceptions=True
            )
        else:
            await self.receive_messages()

    async def stop(self):
        logger.info("Stopping client...")
        if self.receive_task:
            self.receive_task.cancel()
        if self.send_task:
            self.send_task.cancel()
        self.writer.close()
        await self.writer.wait_closed()
        logger.info("Client stopped.")


def _cli_message_callback(message: str):
    print(f"\n{message}")
    sys.stdout.write("> ")
    sys.stdout.flush()


async def main_coro(mode):
    try:
        await client.start(mode)
    except asyncio.CancelledError:
        await client.stop()


if __name__ == "__main__":
    import argparse

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
    client = Client(host=args.host, port=args.port, alias=args.alias)
    client.set_message_callback(_cli_message_callback)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_task = asyncio.ensure_future(main_coro(mode="cli"))
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()
