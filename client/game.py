import socket

import logging
import pygame
import networking
import gui


class Game:
    def __init__(self, surface: pygame.Surface, client_socket: socket.socket):
        self.client_socket = client_socket
        self.surface = surface
        self.ships = []
        self.board_size = None

    def run_setup(self):
        board_size_packet = networking.RecvMessage(self.client_socket)
        board_size_packet.recv_blocking()

        if board_size_packet.error:
            logging.critical("Error when trying to receive board size")
            exit(1)

        try:
            self.board_size = int(board_size_packet.message)

        except TypeError:
            logging.critical(f"Cannot convert {board_size_packet.message} to an int when trying to parse board size")
            exit(1)

        ship_setup = gui.DecideShipsGui(self.board_size, self.surface)
        self.ships = ship_setup.run()

        server_ship_locations = []

        for ship in self.ships:
            server_ship_locations.append([ship.name])

            for coord in ship.coordinates:
                server_ship_locations[-1].append([coord.x, coord.y])

        send_message = networking.SendMessage(self.client_socket)
        send_message.send(server_ship_locations)

        start_message = networking.RecvMessage(self.client_socket)
        start_message.receive()

        clock = pygame.time.Clock()

        while not start_message.received:
            pygame.event.get()  # ignore all events
            ship_setup.draw()
            clock.tick(60)

        print("got start message")

    def run(self):
        self.run_setup()
        print("exited run setup")
        main_gui = gui.MainGui(self.ships, self.board_size, self.surface, self.client_socket)
        main_gui.run()
