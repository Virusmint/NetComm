import asyncio
from typing import Optional, Callable
import ssl

from .protocol.io import write_message, read_message


class Client:
    def __init__(self, host="127.0.0.1", port=50000, alias="Anonymous", tls=False):
        self.host = host
        self.port = port
        self.alias = alias
        self.tls = tls
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.message_callback: Optional[Callable[[str], None]] = None

    def set_message_callback(self, callback: Callable[[str], None]):
        self.message_callback = callback

    async def connect(self):
        ssl_context = None
        if self.tls:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False  # For local IPs
            ssl_context.verify_mode = ssl.CERT_NONE  # Skip certificate verification
        self.reader, self.writer = await asyncio.open_connection(
            self.host, self.port, ssl=ssl_context
        )
        await self.send_message(f"__alias__:{self.alias}")

    async def send_message(self, message: str):
        await write_message(self.writer, message)

    async def receive_message(self):
        message = await read_message(self.reader)
        if self.message_callback:
            self.message_callback(message)
        return message
