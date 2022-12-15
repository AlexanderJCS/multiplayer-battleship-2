import socket

import pygame.surface

import constants
import game

IP = input("IP: ")
PORT = 9850

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.settimeout(1000)


def main():
    pygame.init()
    surface = pygame.display.set_mode((constants.GUI_WIDTH, constants.GUI_HEIGHT))

    g = game.Game(surface, client_socket)
    g.run()


if __name__ == "__main__":
    main()
