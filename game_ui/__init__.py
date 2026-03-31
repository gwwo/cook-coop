from .ui import GameUI
from pyglet.window import key
from game import Action

USER_KEYBOARD_MAP = {
    "1": {
        key.RIGHT: Action.RIGHT,
        key.LEFT: Action.LEFT,
        key.UP: Action.UP,
        key.DOWN: Action.DOWN,
        key.RSHIFT: Action.INTERACT,
    },
    "2": {
        key.D: Action.RIGHT,
        key.A: Action.LEFT,
        key.W: Action.UP,
        key.S: Action.DOWN,
        key.LSHIFT: Action.INTERACT,
    },
    "3": {
        key.L: Action.RIGHT,
        key.J: Action.LEFT,
        key.I: Action.UP,
        key.K: Action.DOWN,
        key.SPACE: Action.INTERACT,
    },
}
