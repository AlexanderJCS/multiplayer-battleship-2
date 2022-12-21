import logging
import socket

import pygame

import connection_gui
import networking
import setup_gui
import main_gui

from settings import settings


class Game:
    def __init__(self, surface: pygame.Surface):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.surface = surface
        self.ships = []
        self.board_size = None

    def connect(self):
        # Run the IP connection screen
        conn = connection_gui.IPConnectionScreen(self.surface, settings["gui"]["gui_width"], 100, self.client_socket)

        while True:
            connected = conn.run()

            if connected:
                break

            # Reset the client socket to avoid errors if the connection failed
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn = connection_gui.IPConnectionScreen(self.surface, settings["gui"]["gui_width"], 100,
                                                     self.client_socket, "Failed")

        self.client_socket.settimeout(1000)

    def get_board_size(self):
        board_size_msg = networking.RecvMessage(self.client_socket)
        board_size_msg.recv_blocking()
        self.board_size = int(board_size_msg.message)

    def run_ship_setup(self):
        ship_setup = setup_gui.SetupGui(self.board_size, self.surface)
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

    def run(self):
        self.connect()
        self.get_board_size()

        while True:
            self.run_ship_setup()
            mg = main_gui.MainGui(self.ships, self.board_size, self.surface, self.client_socket)
            mg.run()
