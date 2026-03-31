import numpy as np


from .pseudo_pixels_5x5 import PIXELS, ITEM_RAW_PIXELS

PIXELS_PER_UNIT = ITEM_RAW_PIXELS  # equals 5

from game import Game


def observe(game: Game):
    w, h = game.kitchen_w, game.kitchen_h
    obs = np.zeros((h * PIXELS_PER_UNIT, w * PIXELS_PER_UNIT), dtype=np.float32)
    for x in range(w):
        for y in range(h):
            counter = game.kitchen[x][y]
            if counter != None:
                holding = counter.describe_holding()
                row, col = PIXELS_PER_UNIT * (h - 1 - y), PIXELS_PER_UNIT * x
                obs[row : row + PIXELS_PER_UNIT, col : col + PIXELS_PER_UNIT] = PIXELS[
                    "counter"
                ][holding]

    position = dict()

    for player in game.players:
        x, y = (
            player.x,
            player.y,
        )
        holding, facing = player.describe_holding(), player.facing
        row, col = int(PIXELS_PER_UNIT * (h - 1 - y)), int(PIXELS_PER_UNIT * x)
        position[player.id] = (row, col)
        obs[row : row + PIXELS_PER_UNIT, col : col + PIXELS_PER_UNIT] = PIXELS["chef"][
            holding
        ][facing]

    obs = obs * 0.5
    all_obs = dict()
    for p_id, (row, col) in position.items():
        my_obs = np.copy(obs)
        my_obs[row : row + PIXELS_PER_UNIT, col : col + PIXELS_PER_UNIT] *= 2
        all_obs[p_id] = my_obs

    return all_obs


def show(obs):
    return "\n".join(
        "".join("  " if v == 0.0 else "██" if v == 1.0 else "GG" for v in r)
        for r in obs
    )
