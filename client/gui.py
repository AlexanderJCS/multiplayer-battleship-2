import logging
import socket

from enum import Enum

import pygame

import constants
import networking

from opponent_board import Board
from ship_coord import ShipCoordinate
from ship import Ship


class Text:
    def __init__(self, message, font, color, pos):
        self.font = font
        self.color = color
        self.pos = pos

        self.text = self.font.render(message, True, self.color)
        self.rect = self.text.get_rect()
        self.rect.center = self.pos

    def draw(self, surface):
        surface.blit(self.text, self.rect)

    def change_text(self, new_text):
        self.text = self.font.render(new_text, True, self.color)
        self.rect = self.text.get_rect()
        self.rect.center = self.pos


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

    def draw_preview_ship(self):
        """
        Draws a "preview ship" that shows where an actual ship would be placed
        """

        # Prevent a KeyError
        if len(self.ship_lengths) == 0:
            return

        mouse_pos = pygame.mouse.get_pos()

        # If the mouse is out of the board
        if mouse_pos[1] >= constants.GUI_WIDTH:
            return

        coords = (int(mouse_pos[0] / constants.GUI_WIDTH * self.board_size),
                  int(mouse_pos[1] / constants.GUI_WIDTH * self.board_size))

        can_be_placed, preview_ship = self.add_ship(coords[0], coords[1],
                                                    self.ship_lengths[-1]["length"],
                                                    self.ship_lengths[-1]["name"])

        # If a ship can be placed at that location
        dist = constants.GUI_WIDTH // self.board_size

        if can_be_placed:
            # Draw the ship
            for coord in preview_ship.coordinates:
                pygame.draw.rect(self.surface, constants.PREVIEW_SHIP_COLOR,
                                 (coord.x * dist + 1, coord.y * dist + 1,
                                  dist - 1, dist - 1))

        else:
            # Draw the ship
            for coord in preview_ship.coordinates:
                if coord.y * dist + 1 >= constants.GUI_WIDTH:
                    break

                pygame.draw.rect(self.surface, constants.PREVIEW_SHIP_CANNOT_PLACE_COLOR,
                                 (coord.x * dist + 1, coord.y * dist + 1,
                                  dist - 1, dist - 1))

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.draw_grid()
        self.draw_ships()
        self.draw_preview_ship()
        pygame.display.update()

    def add_ship(self, x: int, y: int, length: int, name: str):
        """
        Adds a ship at the given x and y coordiantes.
        :param x: The x coord of the ship.
        :param y: The y coord of ths ship.
        :param length: The length of the ship
        :param name: The name of the ship
        :return: (if the ship can be placed, the ship object)
        """
        can_be_placed = True

        if self.place_horizontal and x + length > self.board_size:
            can_be_placed = False

        if not self.place_horizontal and y + length > self.board_size:
            can_be_placed = False

        coordinates = []

        for i in range(length):
            if self.place_horizontal:
                coordinates.append(ShipCoordinate(x + i, y))

            else:
                coordinates.append(ShipCoordinate(x, y + i))

        # Check if the ship overlaps with any other ship
        # and if it does, can_be_placed will be false
        for ship in self.ships:
            for coord1 in coordinates:
                for coord2 in ship.coordinates:
                    if coord1.x == coord2.x and coord1.y == coord2.y:
                        return False, Ship(coordinates, name)

        return can_be_placed, Ship(coordinates, name)

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

            can_be_placed, ship = self.add_ship(coords[0], coords[1], ship_len, ship_name)

            if can_be_placed:
                self.ships.append(ship)
                self.ship_lengths.pop()

        if event.type == pygame.KEYDOWN:
            self.handle_keys_pressed(pygame.key.get_pressed())

    def handle_keys_pressed(self, keys):
        """
        :param keys: The keys currently being pressed, this can be accessed using pygame.key.get_pressed()
        """

        if keys[pygame.K_r]:
            self.place_horizontal = not self.place_horizontal

    def run(self) -> list:
        """
        :return: A list of ship objects to be fed into the MainGui class
        """

        clock = pygame.time.Clock()

        while len(self.ship_lengths) > 0:
            for event in pygame.event.get():
                if len(self.ship_lengths) > 0:
                    self.handle_event(event, self.ship_lengths[-1]["length"], self.ship_lengths[-1]["name"])

            self.draw()
            clock.tick(60)

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
        self.turn_text = Text("Waiting for other player", pygame.font.SysFont("Calibri", 25),
                              (255, 255, 255), (constants.GUI_WIDTH // 2, constants.Y_OFFSET - 75))
        self.ship_destroy_text = Text("", pygame.font.SysFont("Calibri", 25),
                                      (255, 255, 255), (constants.GUI_WIDTH // 2, constants.Y_OFFSET - 25))

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

    def draw_preview_move(self):
        mouse_pos = pygame.mouse.get_pos()

        if mouse_pos[1] <= constants.Y_OFFSET:
            return

        dist = constants.GUI_WIDTH // self.board_size

        coords = (int(mouse_pos[0] / constants.GUI_WIDTH * self.board_size),
                  int((mouse_pos[1] - constants.Y_OFFSET) / constants.GUI_WIDTH * self.board_size))

        pygame.draw.rect(self.surface, constants.PREVIEW_SHIP_COLOR,
                         (coords[0] * dist + 1, coords[1] * dist + constants.Y_OFFSET + 1,
                          dist - 1, dist - 1))

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.draw_player_board()
        self.draw_opponent_board()

        if self.mode == Mode.SELECTING_MOVE:
            self.draw_preview_move()

        self.turn_text.draw(self.surface)
        self.ship_destroy_text.draw(self.surface)

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
        clock = pygame.time.Clock()

        while True:
            opponent_move_info = networking.RecvMessage(self.client_socket)
            opponent_move_info.receive()

            while not opponent_move_info.received:
                self.draw()
                pygame.event.get()  # ignore all events during this time
                clock.tick(60)

            self.mode = Mode.SELECTING_MOVE

            if opponent_move_info.message != "waiting for move":
                for ship in self.ships:
                    if ship.has_coords(*opponent_move_info.message):
                        self.add_opponent_hit(*opponent_move_info.message)
                        break

                else:  # nobreak
                    self.board.add_miss(*opponent_move_info.message)

            self.turn_text.change_text("Your turn")

            while self.mode == Mode.SELECTING_MOVE:
                self.draw()

                for event in pygame.event.get():
                    self.handle_event(event)

                clock.tick(60)

            sunk_status = networking.RecvMessage(self.client_socket)
            sunk_status.recv_blocking()

            self.turn_text.change_text("Waiting for other player")

            if sunk_status.message != "no ship sank":
                self.ship_destroy_text.change_text(sunk_status.message)
