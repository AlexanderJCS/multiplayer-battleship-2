import pygame.surface

import constants
import game


def main():
    pygame.init()
    pygame.display.set_caption("Multiplayer Battleship")
    surface = pygame.display.set_mode((constants.GUI_WIDTH, constants.GUI_HEIGHT))

    g = game.Game(surface)
    g.run()


if __name__ == "__main__":
    main()
