import pygame

import constants


class Ship:
    def __init__(self, coordinates: list, name: str):
        self.coordinates = coordinates
        self.name = name

    def is_sunk(self) -> bool:
        return all(coord.hit for coord in self.coordinates)

    def hit(self, x: int, y: int) -> bool:
        """
        Hits a ship if the x and y coordinate lands on a ship and returns True,
        otherwise does nothing and returns False

        :param x: The x coordiante of the square to attack
        :param y: The y coordiante of the square to attack
        :return: Whether it was a hit or miss
        """

        for coord in self.coordinates:
            if coord.x == x and coord.y == y:
                coord.hit = True
                return True

        return False

    def has_coords(self, x, y):
        return any(coord.x == x and coord.y == y for coord in self.coordinates)

    def draw(self, surface, board_size):
        dist = constants.GUI_WIDTH // board_size

        for coord in self.coordinates:
            pygame.draw.rect(surface, constants.SHIP_COLOR,
                             (coord.x * dist + 1, coord.y * dist + 1,
                              dist - 1, dist - 1))
