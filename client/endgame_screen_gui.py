import pygame

import constants
import gui_text


class EndgameScreenGui:
    def __init__(self, surface, board_size, message, player_board, opponent_board):
        self.surface = surface
        self.board_size = board_size
        self.won_text = gui_text.Text(message, constants.FONT, (255, 255, 255),
                                      (constants.GUI_WIDTH // 2, constants.Y_OFFSET - 75))

        self.info_text = gui_text.Text("Press any key to play again", constants.FONT, (255, 255, 255),
                                       (constants.GUI_WIDTH // 2, constants.Y_OFFSET - 25))

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

        self.won_text.draw(self.surface)
        self.info_text.draw(self.surface)

        pygame.display.update()

    def run(self):
        clock = pygame.time.Clock()
        waiting_for_input = True

        while waiting_for_input:
            self._draw()

            events = pygame.event.get()

            clock.tick(60)  # tick clock here, so you don't have to wait 1 frame after key press

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN:
                    waiting_for_input = False
