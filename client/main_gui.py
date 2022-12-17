import logging
import socket

from enum import Enum

import pygame

import constants
import networking

from board import Board
from gui_text import Text


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

    def _fire(self, x, y):
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

    def _handle_event(self, event: pygame.event):
        if self.mode == Mode.SELECTING_MOVE and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # If it is out of the board
            if mouse_pos[1] <= constants.Y_OFFSET:
                return

            coords = (int(mouse_pos[0] / constants.GUI_WIDTH * self.board_size),
                      int((mouse_pos[1] - constants.Y_OFFSET) / constants.GUI_WIDTH * self.board_size))

            self._fire(*coords)
            self.mode = Mode.WAITING_FOR_MSG

    def _draw_grid(self, y_offset=0):
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

    def _draw_player_board(self):
        self._draw_grid()

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

    def _draw_opponent_board(self):
        self._draw_grid(constants.Y_OFFSET)

        dist = constants.GUI_WIDTH // self.board_size

        for hit in self.opponent_board.hits:
            pygame.draw.rect(self.surface, constants.HIT_COLOR,
                             (hit[0] * dist + 1, hit[1] * dist + constants.Y_OFFSET + 1,
                              dist - 1, dist - 1))

        for miss in self.opponent_board.misses:
            pygame.draw.rect(self.surface, constants.MISS_COLOR,
                             (miss[0] * dist + 1, miss[1] * dist + constants.Y_OFFSET + 1,
                              dist - 1, dist - 1))

    def _draw_preview_move(self):
        mouse_pos = pygame.mouse.get_pos()

        if mouse_pos[1] <= constants.Y_OFFSET:
            return

        dist = constants.GUI_WIDTH // self.board_size

        coords = (int(mouse_pos[0] / constants.GUI_WIDTH * self.board_size),
                  int((mouse_pos[1] - constants.Y_OFFSET) / constants.GUI_WIDTH * self.board_size))

        pygame.draw.rect(self.surface, constants.PREVIEW_SHIP_COLOR,
                         (coords[0] * dist + 1, coords[1] * dist + constants.Y_OFFSET + 1,
                          dist - 1, dist - 1))

    def _draw(self):
        self.surface.fill((0, 0, 0))
        self._draw_player_board()
        self._draw_opponent_board()

        if self.mode == Mode.SELECTING_MOVE:
            self._draw_preview_move()

        self.turn_text.draw(self.surface)
        self.ship_destroy_text.draw(self.surface)

        pygame.display.update()

    def _add_opponent_hit(self, x, y):
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
                self._draw()
                pygame.event.get()  # ignore all events during this time
                clock.tick(60)

            self.mode = Mode.SELECTING_MOVE

            if opponent_move_info.message != "waiting for move":
                for ship in self.ships:
                    if ship.has_coords(*opponent_move_info.message):
                        self._add_opponent_hit(*opponent_move_info.message)
                        break

                else:  # nobreak
                    self.board.add_miss(*opponent_move_info.message)

            self.turn_text.change_text("Your turn")

            while self.mode == Mode.SELECTING_MOVE:
                self._draw()

                for event in pygame.event.get():
                    self._handle_event(event)

                clock.tick(60)

            sunk_status = networking.RecvMessage(self.client_socket)
            sunk_status.recv_blocking()

            self.turn_text.change_text("Waiting for other player")

            if sunk_status.message != "no ship sank":
                self.ship_destroy_text.change_text(sunk_status.message)
