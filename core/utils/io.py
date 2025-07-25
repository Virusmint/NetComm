import asyncio
import struct


class ConnectionCloseError(Exception):
    pass


async def write_message(writer: asyncio.StreamWriter, message: str):
    message = message.encode()
    writer.write(struct.pack("!I", len(message)))
    writer.write(message)
    await writer.drain()


async def read_message(reader: asyncio.StreamReader) -> str:
    header = await reader.readexactly(4)
    if not header:
        raise ConnectionCloseError
    length_data = struct.unpack("!I", header)[0]
    data = await reader.readexactly(length_data)
    return data.decode()
