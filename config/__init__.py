import pathlib
from typing import Union

from game import Player
from game.roles import Pot, Counter, Dish, Server, Ingredient


def load(layout_name: str):
    with open(pathlib.Path(__file__).parent / (layout_name + ".txt"), "r") as f:
        lines = [l_ for l in f if (l_ := l.strip())]
    assert all(len(lines[0]) == len(l) for l in lines[1:])

    # origin at the left lower corner;
    # the coordinate (x, y) has the char of `layout[x][y]`
    layout = list(map(list, zip(*reversed(lines))))

    kitchen: list[list[Union[Counter, None]]] = []
    players: list[Player] = []
    pots: list[Pot] = []

    for x, col in enumerate(layout):
        c = []
        for y, char in enumerate(col):
            tile = None
            if char == "X":
                tile = Counter(holding=None)
            elif char == "P":
                pot = Pot()
                pots.append(pot)
                tile = Counter(holding=pot)
            elif char == "D":
                tile = Counter(holding=Dish(), dispense_new_one=True)
            elif char == "S":
                server = Server(can_serve_ingredient=layout_name.startswith("simple"))
                tile = Counter(holding=server)
            elif char in ["T"]:
                tile = Counter(
                    holding=Ingredient(value="tomato"), dispense_new_one=True
                )
            elif char in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                players.append(Player(x, y, id=char))
            c.append(tile)
        kitchen.append(c)
    return kitchen, players, pots
