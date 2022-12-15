

class Board:
    def __init__(self, size: int, ships: list):
        self.size = size
        self.ships = ships

    def is_lost(self) -> bool:
        return all(ship.is_sunk() for ship in self.ships)

    def fire_at(self, x, y) -> str:
        """
        Fires at a certain x and y position. If it is a hit, it damages the ship.

        :param x: The x coordinate to fire a shell at
        :param y: The y coordinate to fire a shell at
        :return: Whether the shell hit a ship (in other words, whether it was a hit)
        """

        hit_ship_name = ""

        for ship in self.ships:
            if ship.hit(x, y):
                hit_ship_name = ship.name

        return hit_ship_name
