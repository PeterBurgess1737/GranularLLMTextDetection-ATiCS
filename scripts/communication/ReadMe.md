# communication

A small helper package for differentiating messages.

Messages are indicated by a byte at the beginning.
These are used to figure out what the rest of the data is, if it exists.

Please note that everything is in **network endian**, indicated by the "!" when using struct format strings.

## Example usage

```python
import socket
import struct

from communication import Message, MessageProtocol, read_n_bytes


## Create some functions to read and create messages

def _DATA_read_rest_of_message_from(sock: socket.socket) -> Message:
    data_length_bytes = read_n_bytes(sock, struct.calcsize("!I"))
    data_length, = struct.unpack("!I", data_length_bytes)
    data = read_n_bytes(sock, data_length)

    return Message(SomeProtocol.DATA, data)


def _DATA_create_message(data: bytes) -> bytes:
    header_bytes = struct.pack("!BI", SomeProtocol.DATA.value, len(data))
    message_bytes = header_bytes + data

    return message_bytes


def _DONE_read_rest_of_message_from() -> Message:
    return Message(SomeProtocol.Done, None)


def _DONE_create_message() -> bytes:
    message_bytes = struct.pack("!B", SomeProtocol.DONE.value)

    return message_bytes


## Create the protocol and bind the functions to those messages

class SomeProtocol(MessageProtocol):
    DATA = 1, _DATA_read_rest_of_message_from, _DATA_create_message
    DONE = 2, _DONE_read_rest_of_message_from, _DONE_create_message
```
