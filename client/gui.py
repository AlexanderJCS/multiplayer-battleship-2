import logging
import socket

from enum import Enum

import pygame

import constants
import networking

from opponent_board import Board
from ship_coord import ShipCoordinate
from ship import Ship


class DecideShipsGui:
    def __init__(self, board_size: int, surface: pygame.Surface):
        self.board_size = board_size
        self.surface = surface
        self.place_horizontal = True

        self.ship_lengths = [
            {"name": "Destroyer", "length": 2},
            {"name": "Submarine", "length": 3},
            {"name": "Cruiser", "length": 3},
            {"name": "Battleship", "length": 4},
            {"name": "Aircraft Carrier", "length": 5}
        ]

        self.ships = []

    def draw_background(self):
        self.surface.fill(constants.WATER_COLOR)

    def draw_ships(self):
        for ship in self.ships:
            for coord in ship.coordinates:
                dist = constants.GUI_WIDTH // self.board_size
                pygame.draw.rect(self.surface, constants.SHIP_COLOR,
                                 (coord.x * dist + 1, coord.y * dist + 1,
                                  dist - 1, dist - 1))

    def draw_grid(self, y_offset=0):
        size_between = constants.GUI_WIDTH // self.board_size

        x = 0
        y = y_offset

        for _ in range(self.board_size + 1):
            # Draw vertical lines
            pygame.draw.line(self.surface, (100, 100, 100),
                             (x, y_offset),
                             (x, self.board_size * size_between + y_offset))

            # Draw horizontal lines
            pygame.draw.line(self.surface, (100, 100, 100), (0, y), (constants.GUI_WIDTH, y))

            x += size_between
            y += size_between

    def draw(self):
        self.draw_grid()
        self.draw_ships()
        pygame.display.update()

    def add_ship(self, x: int, y: int, length: int, name: str) -> bool:
        """
        Adds a ship at the given x and y coordiantes.
        :param x: The x coord of the ship.
        :param y: The y coord of ths ship.
        :param length: The length of the ship
        :param name: The name of the ship
        :return: Whether the ship was added or not
        """
        if self.place_horizontal and x + length > self.board_size:
            return False

        if not self.place_horizontal and y + length > self.board_size:
            return False

        coordinates = []

        for i in range(length):
            if self.place_horizontal:
                coordinates.append(ShipCoordinate(x + i, y))

            else:
                coordinates.append(ShipCoordinate(x, y + i))

        self.ships.append(Ship(coordinates, name))

        return True

    def handle_event(self, event: pygame.event, ship_len: int, ship_name: str):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # If it is out of the board
            if mouse_pos[1] >= constants.GUI_WIDTH:
                return

            coords = (int(mouse_pos[0] / constants.GUI_WIDTH * self.board_size),
                      int(mouse_pos[1] / constants.GUI_WIDTH * self.board_size))

            if self.add_ship(coords[0], coords[1], ship_len, ship_name):
                self.ship_lengths.pop()

    def handle_keys_pressed(self, keys) -> bool:
        """
        :param keys: The keys currently being pressed, this can be accessed using pygame.key.get_pressed()
        :return: Whether the class should exit the run method
        """

        if keys[pygame.K_r]:
            self.place_horizontal = not self.place_horizontal
            return False

        if keys[pygame.K_RETURN]:
            return True

    def run(self) -> list:
        """
        :return: A list of ship objects to be fed into the MainGui class
        """

        while len(self.ship_lengths) > 0:
            for event in pygame.event.get():
                self.handle_event(event, self.ship_lengths[-1]["length"], self.ship_lengths[-1]["name"])

            if self.handle_keys_pressed(pygame.key.get_pressed()):
                break

            self.draw()

        return self.ships


class Mode(Enum):
    WAITING_FOR_MSG = 1
    SELECTING_MOVE = 2


class MainGui:
    def __init__(self, ships: list, board_size: int, surface: pygame.Surface, client_socket: socket.socket):
        self.ships = ships
        self.board_size = board_size
        self.surface = surface
        self.mode: Mode = Mode.WAITING_FOR_MSG
        self.client_socket = client_socket
        self.board: Board = Board()
        self.opponent_board: Board = Board()
        self.hit_info = networking.RecvMessage(self.client_socket)
        self.opponent_move_info = networking.RecvMessage(self.client_socket)

    def fire(self, x, y):
        fire_message = networking.SendMessage(self.client_socket)
        fire_message.send([x, y])

        if fire_message.error:
            logging.critical(f"Error when trying to send a fire message at coords {[x, y]}")
            exit(1)

        hit_msg = networking.RecvMessage(self.client_socket)
        hit_msg.recv_blocking()

        if hit_msg.message == "hit":
            self.opponent_board.add_hit(x, y)

        else:
            self.opponent_board.add_miss(x, y)

    def get_info(self):
        self.hit_info = networking.RecvMessage(self.client_socket)
        self.hit_info.receive()

        self.opponent_move_info = networking.RecvMessage(self.client_socket)
        self.opponent_move_info.receive()

    def get_turn_info(self):
        pass

    def handle_event(self, event: pygame.event):
        if self.mode == Mode.SELECTING_MOVE and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # If it is out of the board
            if mouse_pos[1] <= constants.Y_OFFSET:
                return

            coords = (int(mouse_pos[0] / constants.GUI_WIDTH * self.board_size),
                      int((mouse_pos[1] - constants.Y_OFFSET) / constants.GUI_WIDTH * self.board_size))

            self.fire(*coords)
            self.mode = Mode.WAITING_FOR_MSG

    def draw_grid(self, y_offset=0):
        size_between = constants.GUI_WIDTH // self.board_size

        x = 0
        y = y_offset

        for _ in range(self.board_size + 1):
            # Draw vertical lines
            pygame.draw.line(self.surface, (100, 100, 100),
                             (x, y_offset),
                             (x, self.board_size * size_between + y_offset))

            # Draw horizontal lines
            pygame.draw.line(self.surface, (100, 100, 100), (0, y), (constants.GUI_WIDTH, y))

            x += size_between
            y += size_between

    def draw_player_board(self):
        self.draw_grid()

        dist = constants.GUI_WIDTH // self.board_size

        for ship in self.ships:
            for coord in ship.coordinates:
                pygame.draw.rect(self.surface, constants.SHIP_COLOR,
                                 (coord.x * dist + 1, coord.y * dist + 1,
                                  dist - 1, dist - 1))

        for hit in self.board.hits:
            pygame.draw.rect(self.surface, constants.HIT_COLOR,
                             (hit[0] * dist + 1, hit[1] * dist + 1,
                              dist - 1, dist - 1))

        for miss in self.board.misses:
            pygame.draw.rect(self.surface, constants.MISS_COLOR,
                             (miss[0] * dist + 1, miss[1] * dist + 1,
                              dist - 1, dist - 1))

    def draw_opponent_board(self):
        self.draw_grid(constants.Y_OFFSET)

        dist = constants.GUI_WIDTH // self.board_size

        for hit in self.opponent_board.hits:
            pygame.draw.rect(self.surface, constants.HIT_COLOR,
                             (hit[0] * dist + 1, hit[1] * dist + constants.Y_OFFSET + 1,
                              dist - 1, dist - 1))

        for miss in self.opponent_board.misses:
            pygame.draw.rect(self.surface, constants.MISS_COLOR,
                             (miss[0] * dist + 1, miss[1] * dist + constants.Y_OFFSET + 1,
                              dist - 1, dist - 1))

    def draw(self):
        self.draw_player_board()
        self.draw_opponent_board()
        pygame.display.update()

    def add_opponent_hit(self, x, y):
        for ship in self.ships:
            for coord in ship.coordinates:
                if coord.x == x and coord.y == y:
                    coord.hit = True
                    self.board.add_hit(x, y)
                    return

        self.board.add_miss(x, y)

    def run(self):
        while True:
            self.opponent_move_info = networking.RecvMessage(self.client_socket)
            self.opponent_move_info.receive()

            while not self.opponent_move_info.received:
                self.draw()
                pygame.event.get()  # ignore all events during this time

            print(self.opponent_move_info.message)
            self.mode = Mode.SELECTING_MOVE

            if self.opponent_move_info.message != "waiting for move":
                for ship in self.ships:
                    if ship.has_coords(*self.opponent_move_info.message):
                        self.add_opponent_hit(*self.opponent_move_info.message)
                        break

                else:  # nobreak
                    self.board.add_miss(*self.opponent_move_info.message)

            while self.mode == Mode.SELECTING_MOVE:
                self.draw()

                for event in pygame.event.get():
                    self.handle_event(event)

            sunk_status = networking.RecvMessage(self.client_socket)
            sunk_status.recv_blocking()

            print(f"Ship sunk status: {sunk_status.message}")
