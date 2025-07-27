import asyncio
import argparse

from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession

from ...networking.client import Client


class ClientCLI:
    def __init__(self, client: Client):
        self.client = client
        self.pending_tasks = None
        self.stop_event = asyncio.Event()
        self.client.set_message_callback(self._message_callback)

    def _message_callback(self, message: str):
        print(f"\r{message}")

    async def send_loop(self):
        session = PromptSession()
        with patch_stdout():
            while True:
                try:
                    message = await session.prompt_async("> ")
                    if message.lower() in ("exit", "quit"):
                        await self.stop()
                        break
                    await self.client.send_message(message)
                except (EOFError, KeyboardInterrupt):
                    self.stop_event.set()
                    break

    async def receive_loop(self):
        while True:
            try:
                message = await self.client.receive_message()
                if message is None:
                    break
            except (asyncio.CancelledError, ConnectionError):
                self.stop_event.set()
                break

    async def start(self):
        try:
            await self.client.connect()
            print(
                f"Connected to {self.client.host}:{self.client.port} as {self.client.alias}"
            )
        except ConnectionError as e:
            print(f"Connection error: {e}")
            return
        self.stop_event.clear()
        _, self.pending_tasks = await asyncio.wait(
            [
                asyncio.create_task(self.receive_loop()),
                asyncio.create_task(self.send_loop()),
                asyncio.create_task(self.stop_event.wait()),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )
        await self.stop()

    async def stop(self):
        if self.pending_tasks:
            for task in self.pending_tasks:
                task.cancel()
        if self.client.writer:
            self.client.writer.close()
            await self.client.writer.wait_closed()
        print("Client disconnected.")


def main():
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
    cli = ClientCLI(client)
    asyncio.run(cli.start())


if __name__ == "__main__":
    main()
