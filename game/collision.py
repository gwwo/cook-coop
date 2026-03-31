import math


class Rect:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x, self.y = x, y
        self.w, self.h = w, h


def check(moving: Rect, fixed: Rect, dx: float, dy: float) -> tuple[float, bool, bool]:
    if dx == 0 and dy == 0:
        return 1, False, False

    x_near = fixed.x - (fixed.w + moving.w) / 2
    x_far = fixed.x + (fixed.w + moving.w) / 2
    y_near = fixed.y - (fixed.h + moving.h) / 2
    y_far = fixed.y + (fixed.h + moving.h) / 2

    if dx < 0:
        x_near, x_far = x_far, x_near
    if dy < 0:
        y_near, y_far = y_far, y_near

    def hit(to_near: float, to_far: float, d: float):
        if d == 0:
            if to_near < 0 and to_far > 0:
                t_near, t_far = -math.inf, math.inf
            else:
                t_near, t_far = math.inf, math.inf
        else:
            t_near, t_far = to_near / d, to_far / d
        return t_near, t_far

    t_near_x, t_far_x = hit(x_near - moving.x, x_far - moving.x, dx)
    t_near_y, t_far_y = hit(y_near - moving.y, y_far - moving.y, dy)

    if t_near_x > t_far_y or t_near_y > t_far_x:
        return 1, False, False

    t_hit_near, t_hit_far = max(t_near_x, t_near_y), min(t_far_x, t_far_y)

    # allow t_hit_near < 0 to deal with float numbers' precision issue
    if t_hit_far <= 0 or t_hit_near >= 1:
        return 1, False, False

    if t_hit_near < -0.001:
        t_hit_near = 0

    dx_0 = t_hit_near == t_near_x
    dy_0 = t_hit_near == t_near_y

    return t_hit_near, dx_0, dy_0
