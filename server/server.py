import logging
import socket

import player
import game

IP = socket.gethostbyname(socket.gethostname())
PORT = 9850

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serversocket.bind((IP, PORT))
serversocket.listen(2)


def main():
    clientsockets = []

    while len(clientsockets) < 2:
        clientsocket, addr = serversocket.accept()
        logging.info(f"Accepted socket with address {addr}")
        clientsockets.append(clientsocket)

    players = [player.Player(clientsocket) for clientsocket in clientsockets]

    while True:
        g = game.Game(players)
        g.send_start_messages()

        while True:
            g.get_ships()
            g.main_game_loop()


if __name__ == "__main__":
    main()
