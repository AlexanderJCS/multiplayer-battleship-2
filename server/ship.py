

class Ship:
    def __init__(self, name: str, coordinates: list):
        self.name = name
        self.coordinates = coordinates

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
