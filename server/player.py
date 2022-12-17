import logging
import json

from board import Board
import constants


class Player:
    def __init__(self, clientsocket):
        self.clientsocket = clientsocket
        self.board = Board(constants.BOARD_SIZE, [])

    def assign_ships(self, ships: list):
        self.board.ships = ships

    def receive(self):
        try:
            header = self.clientsocket.recv(constants.HEADERSIZE)

            if header == b"":
                logging.critical("Socket disconnected")
                return "Client disconnected"

            message_length = int(header.decode('utf-8').strip())
            message = self.clientsocket.recv(message_length)

        except (ConnectionResetError, ConnectionAbortedError):
            logging.critical("Connection reset or connection aborted error: socket disconnected")
            return "Client disconnected"

        return json.loads(message)

    def send(self, message):
        logging.info(f"Sending message {message}")

        message = json.dumps(message, ensure_ascii=False).encode("utf-8")
        header_info = f"{len(message):<{constants.HEADERSIZE}}".encode("utf-8")

        try:
            self.clientsocket.send(header_info)
            self.clientsocket.send(message)
            return True

        except ConnectionResetError:
            return False
