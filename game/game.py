from enum import Enum
import math
from copy import deepcopy
from dataclasses import dataclass

from typing import Union, Literal
from .movement import Movable, Wall, move
from .roles import Chef, Counter, Pot


class Player(Chef):
    def __init__(self, x: float, y: float, id: str):
        super().__init__()
        self.x, self.y, self.id = x, y, id
        self.facing: Literal["south", "north", "east", "west"] = "south"


@dataclass
class ActionValue:
    turn: Literal["south", "north", "east", "west"]
    and_interact: bool
    then_move: tuple[float, float]  # dx, dy


class Action(Enum):
    NOOP = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    INTERACT = 5

    def compute(
        self, player: Player, move_to_axis: bool, move_stride: float
    ) -> ActionValue:
        turn, and_interact = player.facing, False
        x, y, dx, dy = player.x, player.y, 0.0, 0.0
        if self == Action.UP:
            dy = math.floor(y) + 1 - y if move_to_axis else move_stride
            turn = "north"
        elif self == Action.DOWN:
            dy = math.ceil(y) - 1 - y if move_to_axis else -move_stride
            turn = "south"
        elif self == Action.RIGHT:
            dx = math.floor(x) + 1 - x if move_to_axis else move_stride
            turn = "east"
        elif self == Action.LEFT:
            dx = math.ceil(x) - 1 - x if move_to_axis else -move_stride
            turn = "west"
        elif self == Action.INTERACT:
            and_interact = True
        return ActionValue(turn, and_interact, then_move=(dx, dy))


class Game:
    def __init__(
        self,
        kitchen: list[list[Union[Counter, None]]],
        players: list[Player],
        pots: list[Pot],
        move_to_axis: bool = False,
        move_stride: float = 0.2,
        player_size: tuple[float, float] = (1.0, 1.0),
    ):
        w, h = len(kitchen), len(kitchen[0])
        assert all(len(col) == h for col in kitchen[1:]), "kitchen not rectangular"
        assert len(set([p.id for p in players])) == len(players), "players not unique"

        self.player_w, self.player_h = player_size
        self.move_to_axis = move_to_axis
        self.move_stride = move_stride
        self.kitchen_w, self.kitchen_h = w, h
        self.player_n = len(players)
        self._kitchen, self._players, self._pots = kitchen, players, pots

    def reset(self):
        self.kitchen = deepcopy(self._kitchen)
        self.players = deepcopy(self._players)
        self.pots = deepcopy(self._pots)
        return self

    def step(self, actions: dict[str, Action]):

        feedbacks = {p.id: 0 for p in self.players}
        events: dict[Player, ActionValue] = {
            p: actions[p.id].compute(p, self.move_to_axis, self.move_stride)
            for p in self.players
        }

        for p, av in events.items():
            p.facing = av.turn
            if av.and_interact:
                counter = self.within_reach(p)
                if counter != None:
                    feedbacks[p.id] += p.interact(counter)

        movable_players: dict[Movable, Player] = dict()

        for p, av in events.items():
            dx, dy = av.then_move
            m = Movable(p.x, p.y, self.player_w, self.player_h, dx, dy)
            movable_players[m] = p

        moved: list[Movable] = self.resolve(movable_players.keys())
        for m in moved:
            p = movable_players[m]
            p.x, p.y = m.x, m.y

        return feedbacks

    def within_reach(self, player: Player) -> Union[Counter, None]:
        x, y = player.x, player.y
        if player.facing in ["north", "south"]:
            if player.facing == "north":
                top = y + self.player_h / 2
                tile_y = math.ceil(top)
                distance = tile_y - 0.5 - top
            elif player.facing == "south":
                bottom = y - self.player_h / 2
                tile_y = math.floor(bottom)
                distance = bottom - (tile_y + 0.5)
            if distance < 0.1 and distance > -0.0001:
                return self.counter_at(round(x), tile_y)
        elif player.facing in ["east", "west"]:
            if player.facing == "east":
                right = x + self.player_w / 2
                tile_x = math.ceil(right)
                distance = tile_x - 0.5 - right
            elif player.facing == "west":
                left = x - self.player_w / 2
                tile_x = math.floor(left)
                distance = left - (tile_x + 0.5)
            if distance < 0.1 and distance > -0.0001:
                return self.counter_at(tile_x, round(y))
        return None

    def counter_at(self, x: int, y: int) -> Union[Counter, None]:
        counter = None
        if x >= 0 and x < self.kitchen_w and y >= 0 and y < self.kitchen_h:
            counter = self.kitchen[x][y]
        return counter

    def resolve(self, movables: list[Movable]) -> list[Movable]:

        need_move: dict[Movable, list[Union[Wall, Movable]]] = dict()

        def _int(real: float, favor_lower=False):
            OFFSET = 0.001  # to handle floating numbers' misterious precision
            if favor_lower:
                return math.ceil(real - 0.5 - OFFSET)
            # otherwise favor upper
            else:
                return math.floor(real + 0.5 + OFFSET)

        processed: list[tuple[Union[Wall, Movable], float, float, float, float]] = []

        for m in movables:
            dx, dy = m.dx, m.dy
            right, left = m.x + m.w / 2, m.x - m.w / 2
            top, bottom = m.y + m.h / 2, m.y - m.h / 2

            l, r, b, t = left, right, bottom, top
            if dx > 0:
                r += dx
                horizontal_sweep = range(_int(right, favor_lower=True) + 1, _int(r) + 1)
            elif dx < 0:
                l += dx
                horizontal_sweep = range(_int(l, favor_lower=True), _int(left))
            if dy > 0:
                t += dy
                vertical_sweep = range(_int(top, favor_lower=True) + 1, _int(t) + 1)
            elif dy < 0:
                b += dy
                vertical_sweep = range(_int(b, favor_lower=True), _int(bottom))

            if dx == 0 and dy == 0:
                m = Wall(m.x, m.y, m.w, m.h)
            else:
                tile_coordinates: list[tuple[int, int]] = []
                if dx != 0:
                    vertical_span = range(_int(bottom, favor_lower=True), _int(top) + 1)
                    tile_coordinates += [
                        (x, y) for x in horizontal_sweep for y in vertical_span
                    ]
                if dy != 0:
                    horizontal_span = range(
                        _int(left, favor_lower=True), _int(right) + 1
                    )
                    tile_coordinates += [
                        (x, y) for x in horizontal_span for y in vertical_sweep
                    ]
                if dx != 0 and dy != 0:
                    tile_coordinates += [
                        (x, y) for x in horizontal_sweep for y in vertical_sweep
                    ]
                # Here, m is always of Movable type
                need_move[m] = [
                    Wall(x, y, w=1, h=1)
                    for x, y in tile_coordinates
                    if self.counter_at(x, y) != None
                ]

            for other, o_l, o_r, o_b, o_t in processed:
                if l < o_r and r > o_l and b < o_t and t > o_b:
                    if type(m) is Movable:
                        need_move[m].append(other)
                    elif type(other) is Movable:
                        need_move[other].append(m)

            processed.append((m, l, r, b, t))

        move(need_move)

        return need_move.keys()
