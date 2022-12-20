import logging
import socket

from enum import Enum

import pygame

import endgame_screen_gui
import constants
import networking

from board import Board
from gui_text import Text


class Mode(Enum):
    WAITING_FOR_MSG = 1
    SELECTING_MOVE = 2


class MainGui:
    def __init__(self, ships: list, board_size: int, surface: pygame.Surface, client_socket: socket.socket):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.board_size = board_size
        self.surface = surface
        self.mode: Mode = Mode.WAITING_FOR_MSG
        self.client_socket = client_socket
        self.board: Board = Board(ships)
        self.opponent_board: Board = Board([])

        self.turn_text = Text("Waiting for other player", constants.FONT,
                              (255, 255, 255), (constants.GUI_WIDTH // 2, constants.Y_OFFSET - 75))

        self.ship_destroy_text = Text("", constants.FONT,
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
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if self.mode == Mode.SELECTING_MOVE and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # If it is out of the board
            if mouse_pos[1] <= constants.Y_OFFSET:
                return

            coords = (int(mouse_pos[0] / constants.GUI_WIDTH * self.board_size),
                      int((mouse_pos[1] - constants.Y_OFFSET) / constants.GUI_WIDTH * self.board_size))

            if not (self.opponent_board.hit_at(*coords) or self.opponent_board.miss_at(*coords)):
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

    def _draw_ships(self):
        for ship in self.board.ships:
            ship.draw(self.surface, self.board_size)

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
        self._draw_ships()
        self.board.draw(self.surface, self.board_size)
        self.opponent_board.draw(self.surface, self.board_size, constants.Y_OFFSET)

        if self.mode == Mode.SELECTING_MOVE:
            self._draw_preview_move()

        self.turn_text.draw(self.surface)
        self.ship_destroy_text.draw(self.surface)

        pygame.display.update()

    def _handle_endgame(self, message):
        send_ships = networking.SendMessage(self.client_socket)
        send_ships.send(self.board.to_dict())

        recv_ships = networking.RecvMessage(self.client_socket)
        recv_ships.recv_blocking()

        opponent_board = Board.from_dict(recv_ships.message)

        endgame_screen = endgame_screen_gui.EndgameScreenGui(self.surface, self.board_size, message["game_status"],
                                                             self.board, opponent_board)
        endgame_screen.run()

    def run(self):
        clock = pygame.time.Clock()

        while True:
            opponent_move_info = networking.RecvMessage(self.client_socket)
            opponent_move_info.receive()

            while not opponent_move_info.received:
                self._draw()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                clock.tick(60)

            self.mode = Mode.SELECTING_MOVE

            if type(opponent_move_info.message) == dict and opponent_move_info.message["game_status"] is not None:
                if opponent_move_info.message["game_status"] == "You lost":
                    self.board.fire_at(*opponent_move_info.message["move"])

                self._handle_endgame(opponent_move_info.message)
                return

            if opponent_move_info.message != "waiting for move":
                self.board.fire_at(*opponent_move_info.message["move"])

            self.turn_text.change_text("Your turn")
            your_turn_sound = pygame.mixer.Sound(file=constants.YOUR_TURN_SOUND_PATH)
            your_turn_sound.play()

            while self.mode == Mode.SELECTING_MOVE:
                self._draw()

                for event in pygame.event.get():
                    self._handle_event(event)

                clock.tick(60)

            sunk_status = networking.RecvMessage(self.client_socket)
            sunk_status.recv_blocking()

            self.turn_text.change_text("Waiting for other player")
            self.ship_destroy_text.change_text("")

            if sunk_status.message != "no ship sank":
                self.ship_destroy_text.change_text(sunk_status.message)
