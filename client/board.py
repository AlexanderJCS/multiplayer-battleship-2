import pygame

from settings import settings
import ship


class Board:
    def __init__(self, ships):
        self.ships = ships
        self.hits = []
        self.misses = []

    def add_hit(self, x: int, y: int):
        self.hits.append((x, y))

    def add_miss(self, x: int, y: int):
        self.misses.append((x, y))

    def hit_at(self, x: int, y: int) -> bool:
        return any(hit[0] == x and hit[1] == y for hit in self.hits)

    def miss_at(self, x: int, y: int) -> bool:
        return any(miss[0] == x and miss[1] == y for miss in self.misses)

    def fire_at(self, x, y):
        for shp in self.ships:
            for coord in shp.coordinates:
                if coord.x == x and coord.y == y:
                    self.add_hit(x, y)
                    return

        self.add_miss(x, y)

    @staticmethod
    def from_dict(board_dict):
        board = Board([])

        board.hits = board_dict["hits"]
        board.misses = board_dict["misses"]
        board.ships = [ship.Ship.from_list(ship_coords) for ship_coords in board_dict["ships"]]

        return board

    def to_dict(self):
        return {
            "hits": self.hits,
            "misses": self.misses,
            "ships": [shp.to_list() for shp in self.ships]
        }

    @staticmethod
    def draw_grid(surface, board_size, y_offset=0):
        size_between = settings["gui"]["gui_width"] // board_size

        x = 0
        y = y_offset

        for _ in range(board_size + 1):
            # Draw vertical lines
            pygame.draw.line(surface, (100, 100, 100),
                             (x, y_offset),
                             (x, board_size * size_between + y_offset))

            # Draw horizontal lines
            pygame.draw.line(surface, (100, 100, 100), (0, y), (settings["gui"]["gui_width"], y))

            x += size_between
            y += size_between

    @staticmethod
    def draw_cubes(surface, coords, color, board_size, y_offset):
        dist = settings["gui"]["gui_width"] // board_size

        for coord in coords:
            pygame.draw.rect(surface, color,
                             (coord[0] * dist + 1, coord[1] * dist + y_offset + 1,
                              dist - 1, dist - 1))

    def draw(self, surface, board_size, y_offset=0):
        self.draw_grid(surface, board_size, y_offset)
        self.draw_cubes(surface, self.hits, settings["colors"]["hit_color"], board_size, y_offset)
        self.draw_cubes(surface, self.misses, settings["colors"]["miss_color"], board_size, y_offset)
