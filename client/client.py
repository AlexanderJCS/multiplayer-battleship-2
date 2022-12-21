import pygame.surface

from settings import settings
import game


def main():
    pygame.init()
    pygame.display.set_caption("Multiplayer Battleship")
    surface = pygame.display.set_mode((settings["gui"]["gui_width"], settings["gui"]["gui_height"]))

    g = game.Game(surface)
    g.run()


if __name__ == "__main__":
    main()
