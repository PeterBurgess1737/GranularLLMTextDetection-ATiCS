import socket


def read_n_bytes(sock: socket.socket, n: int) -> bytes:
    """
    A helper function to receive a specific number of bytes from a socket.

    :param sock: The socket object used to receive data.
    :param n: The number of bytes to read from the socket.
    :return: A bytes object containing the data received from the socket.
    """

    received_bytes = bytes()
    while len(received_bytes) < n:
        received_bytes += sock.recv(n - len(received_bytes))
    return received_bytes
