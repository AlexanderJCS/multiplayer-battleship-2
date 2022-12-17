import pygame

if not pygame.font.get_init():
    pygame.font.init()

FONT = pygame.font.SysFont("Calibri", 25)

GUI_WIDTH = 400
GUI_HEIGHT = 900
Y_OFFSET = GUI_WIDTH + 100

WATER_COLOR = (53, 220, 242)
SHIP_COLOR = (149, 168, 173)
PREVIEW_SHIP_COLOR = (80, 90, 90)
PREVIEW_SHIP_CANNOT_PLACE_COLOR = (200, 20, 20)
HIT_COLOR = (255, 50, 50)
MISS_COLOR = (230, 230, 230)
