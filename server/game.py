import ship_coord
import constants
import ship


class Game:
    def __init__(self, players: list):
        self.players = players

    def setup(self):
        for player in self.players:
            player.send(str(constants.BOARD_SIZE))

        for player in self.players:
            ships = player.receive()
            ships_objects = []

            for ship_coords in ships:
                print(ship_coords)
                coords_object = [ship_coord.ShipCoordinate(*coord) for coord in ship_coords[1:]]

                for coord in coords_object:
                    print(coord.x, coord.y)

                ships_objects.append(ship.Ship(ship_coords[0], coords_object))

            player.assign_ships(ships_objects)

    def main_game_loop(self):
        for player in self.players:
            player.send("starting")

        game_ended = False

        self.players[0].send("waiting for move")

        while not game_ended:
            for i, player in enumerate(self.players):
                print(f"Sending waiting for move to player {i}")

                move = player.receive()  # this will be a list: [x, y]
                print("Received move")

                print(move)

                ship_hit = self.players[i - 1].board.fire_at(*move)

                player.send("hit" if ship_hit else "miss")

                sunk = False

                for ship_obj in self.players[i - 1].board.ships:
                    if ship_obj.name == ship_hit and ship_obj.is_sunk():
                        sunk = True

                if sunk:
                    player.send(f"sunk {ship_hit}")

                else:
                    player.send("no ship sank")

                if self.players[i - 1].board.is_lost():
                    player.send("won")
                    self.players[i - 1].send("lost")
                    game_ended = True
                    break

                print(f"Sending to player {i - 1}")
                self.players[i - 1].send([move[0], move[1]])
