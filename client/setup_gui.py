import pygame

import constants

from ship_coord import ShipCoordinate
from ship import Ship


class SetupGui:
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

    def _draw_background(self):
        self.surface.fill(constants.WATER_COLOR)

    def _draw_ships(self):
        for ship in self.ships:
            for coord in ship.coordinates:
                dist = constants.GUI_WIDTH // self.board_size
                pygame.draw.rect(self.surface, constants.SHIP_COLOR,
                                 (coord.x * dist + 1, coord.y * dist + 1,
                                  dist - 1, dist - 1))

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

    def _draw_preview_ship(self):
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

        can_be_placed, preview_ship = self._add_ship(coords[0], coords[1],
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
        self._draw_grid()
        self._draw_ships()
        self._draw_preview_ship()
        pygame.display.update()

    def _add_ship(self, x: int, y: int, length: int, name: str):
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

    def _handle_event(self, event: pygame.event, ship_len: int, ship_name: str):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # If it is out of the board
            if mouse_pos[1] >= constants.GUI_WIDTH:
                return

            coords = (int(mouse_pos[0] / constants.GUI_WIDTH * self.board_size),
                      int(mouse_pos[1] / constants.GUI_WIDTH * self.board_size))

            can_be_placed, ship = self._add_ship(coords[0], coords[1], ship_len, ship_name)

            if can_be_placed:
                self.ships.append(ship)
                self.ship_lengths.pop()

        if event.type == pygame.KEYDOWN:
            self._handle_keys_pressed(pygame.key.get_pressed())

    def _handle_keys_pressed(self, keys):
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
                    self._handle_event(event, self.ship_lengths[-1]["length"], self.ship_lengths[-1]["name"])

            self.draw()
            clock.tick(60)

        return self.ships
