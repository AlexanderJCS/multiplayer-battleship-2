import threading
import logging
import socket
import json


HEADERSIZE = 10


class RecvMessage:
    def __init__(self, client_socket: socket.socket):
        self.received = False
        self.message = None
        self.error = False
        self.client_socket = client_socket

    def receive(self):
        t = threading.Thread(target=self.recv_blocking)
        t.start()

    def recv_blocking(self):
        logging.debug("Attemting to receive packet")

        try:
            header = self.client_socket.recv(HEADERSIZE)

            if header == b"":
                logging.critical("Server disconnected")
                self.error = True
                return

            message_length = int(header.decode('utf-8').strip())
            message = self.client_socket.recv(message_length)

        except (ConnectionResetError, ConnectionAbortedError) as e:
            logging.exception(e)
            self.error = True
            return

        self.received = True
        self.message = json.loads(message)


class SendMessage:
    def __init__(self, client_socket: socket.socket):
        self.sent = False
        self.error = False
        self.client_socket = client_socket

    def send(self, message):
        logging.info(f"Sending message {message}")

        message = json.dumps(message, ensure_ascii=False).encode("utf-8")
        header_info = f"{len(message):<{HEADERSIZE}}".encode("utf-8")

        try:
            self.client_socket.send(header_info)
            self.client_socket.send(message)
            self.sent = True

        except ConnectionResetError:
            self.error = True
