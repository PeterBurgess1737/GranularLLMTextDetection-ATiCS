import socket
import struct

from scripts.communication import MessageProtocol, Message, read_n_bytes


def _TERMINATE_read_rest_of_message_from() -> Message:
    return Message(MainProtocol.TERMINATE, None)


def _TERMINATE_create_message() -> bytes:
    return struct.pack("!B", MainProtocol.TERMINATE.value)


def _TEXT_read_rest_of_message_from(sock: socket.socket) -> Message:
    text_length_bytes = read_n_bytes(sock, 4)
    text_length, = struct.unpack("!I", text_length_bytes)

    text_bytes = read_n_bytes(sock, text_length)
    text = text_bytes.decode("utf-8")

    return Message(MainProtocol.TEXT, text)


def _TEXT_create_message(text: str) -> bytes:
    text_bytes = text.encode()
    message_header = struct.pack("!BI", MainProtocol.TEXT.value, len(text_bytes))

    return message_header + text_bytes


class MainProtocol(MessageProtocol):
    TERMINATE = 0, _TERMINATE_read_rest_of_message_from, _TERMINATE_create_message
    TEXT = 1, _TEXT_read_rest_of_message_from, _TEXT_create_message
