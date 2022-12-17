

class Board:
    def __init__(self):
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
