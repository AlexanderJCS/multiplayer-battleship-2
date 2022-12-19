import time

import pygame

import constants
import gui_text


class EndgameScreenGui:
    def __init__(self, surface, board_size, message, player_board, opponent_board):
        self.surface = surface
        self.board_size = board_size
        self.text = gui_text.Text(message, constants.FONT, (255, 255, 255),
                                  (constants.GUI_WIDTH // 2, constants.Y_OFFSET - 50))
        self.player_board = player_board
        self.opponent_board = opponent_board

    def _draw(self):
        self.surface.fill((0, 0, 0))

        for ship in self.player_board.ships:
            ship.draw(self.surface, self.board_size)

        for ship in self.opponent_board.ships:
            ship.draw(self.surface, self.board_size, constants.Y_OFFSET)

        self.player_board.draw(self.surface, self.board_size)
        self.opponent_board.draw(self.surface, self.board_size, constants.Y_OFFSET)

        self.text.draw(self.surface)
        pygame.display.update()

    def run(self, wait_time):
        clock = pygame.time.Clock()
        start_time = time.time()

        while time.time() - start_time <= wait_time:
            self._draw()
            clock.tick(60)
