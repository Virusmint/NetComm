import asyncio
import struct
from typing import Union

MAX_MESSAGE_LENGTH = 1024


async def write_message(
    writer: asyncio.StreamWriter, message: Union[str, bytes]
) -> None:
    """Write a message to the stream.

    Args:
        writer (asyncio.StreamWriter): The stream writer to write to.
        message (Union[str, bytes]): The message to write. If a string is provided, it will be encoded to bytes.
    Raises:
        ConnectionError: If the writer is closing.
    """
    if writer.is_closing():
        raise ConnectionError
    if isinstance(message, str):
        message = message.encode()
    writer.write(struct.pack("!I", len(message)))
    writer.write(message)
    await writer.drain()


async def read_message(reader: asyncio.StreamReader) -> str:
    """Read a message from the stream.

    Args:
        reader (asyncio.StreamReader): The stream reader to read from.
    Returns:
        str: The decoded message.
    Raises:
        ConnectionError: If the connection is closed before reading the message.
    """
    try:
        header = await reader.readexactly(4)
        length_data = struct.unpack("!I", header)[0]
        if length_data > MAX_MESSAGE_LENGTH:
            length_data = MAX_MESSAGE_LENGTH
        data = await reader.readexactly(length_data)
    except asyncio.IncompleteReadError:
        raise ConnectionError
    return data.decode()
