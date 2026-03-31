from typing import Union

from .collision import Rect, check

Wall = Rect


class Movable(Rect):
    def __init__(self, x: float, y: float, w: float, h: float, dx: float, dy: float):
        super().__init__(x, y, w, h)
        self.dx, self.dy = dx, dy


# during movement, each `movable` has concerns for other entities that it may collide with
Concern = Union[Wall, Movable]
# `movable` receives responses, because it's concerned about others or because it concerns others;
# once it resolves a response, it need not be concerned about the associated other anymore.
Response = tuple[Union[Concern, None], float, bool, bool]


def move(movables: dict[Movable, list[Union[Wall, Movable]]]):

    assert all(
        all(c in movables for c in cs if type(c) is Movable) for cs in movables.values()
    )

    while True:
        t_next = 1
        responses_of: dict[Movable, list[Response]] = {m: [] for m in movables}

        for m in movables:
            concerns_remain: list[Concern] = []

            for c in movables[m]:
                # no concern if both have stopped
                if m.dx == 0 and m.dy == 0:
                    if type(c) is Wall:
                        continue
                    elif type(c) is Movable and c.dx == 0 and c.dy == 0:
                        continue
                concerns_remain.append(c)

                dx, dy = m.dx, m.dy
                if type(c) is Movable:
                    dx, dy = dx - c.dx, dy - c.dy

                t, dx_0, dy_0 = check(m, c, dx, dy)

                # still send response to self even if self has stopped and other has not
                # for later removing the concern after actual collision
                responses_of[m].append((c, t, dx_0, dy_0))
                if type(c) is Movable:
                    responses_of[c].append((None, t, dx_0, dy_0))

                if t < t_next:
                    t_next = t

            movables[m] = concerns_remain

        for m in movables:
            if m.dx != 0:
                m.x += m.dx * t_next
                m.dx = m.dx * (1 - t_next)
            if m.dy != 0:
                m.y += m.dy * t_next
                m.dy = m.dy * (1 - t_next)
            if t_next == 1:
                continue

            concerns_remain: list[Concern] = []
            for c, t, dx_0, dy_0 in responses_of[m]:
                # no concern after actual collision
                if t == t_next:
                    if dx_0:
                        m.dx = 0
                    if dy_0:
                        m.dy = 0
                elif c != None:
                    concerns_remain.append(c)
            movables[m] = concerns_remain

        if t_next == 1:
            break
