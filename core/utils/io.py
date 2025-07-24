import asyncio
import struct


class MessageReadError(Exception):
    pass


async def read_message(reader: asyncio.StreamReader) -> str:
    try:
        header = await reader.readexactly(4)
        if not header:
            raise MessageReadError("Empty header received")
        length_data = struct.unpack("!I", header)[0]
        data = await reader.readexactly(length_data)
        return data.decode()
    except (asyncio.IncompleteReadError, struct.error, UnicodeDecodeError) as e:
        raise MessageReadError(f"Failed to read message: {e}")
