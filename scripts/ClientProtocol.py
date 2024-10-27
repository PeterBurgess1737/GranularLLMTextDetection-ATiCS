import socket
import struct

from scripts.communication import MessageProtocol, Message, read_n_bytes


def _EVALUATION_read_rest_of_message_from(sock: socket.socket) -> Message:
    evaluation_bytes = read_n_bytes(sock, struct.calcsize("!ff"))
    crit_and_prob = struct.unpack("!ff", evaluation_bytes)

    return Message(ClientProtocol.EVALUATION, crit_and_prob)


class ClientProtocol(MessageProtocol):
    EVALUATION = 1, _EVALUATION_read_rest_of_message_from, ...
    # No need for a create message function as the client script cannot import this
