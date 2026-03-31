import pyglet
import time
from typing import Union
from game import Action, Game, Player
from game.roles import Counter

from .sprites import CounterSprite, PlayerSprite, FloorSprite, PIXELS_PER_UNIT


class GameUI:
    def __init__(
        self,
        game: Game,
        keyboard_map: Union[dict[str, dict[int, Action]], None] = None,
        caption: Union[str, None] = None,
    ):
        w, h = game.kitchen_w, game.kitchen_h
        caption = caption or "wellcooked"
        self.window = pyglet.window.Window(
            w * PIXELS_PER_UNIT, h * PIXELS_PER_UNIT, caption
        )
        # Fix HiDPI/Retina: use logical pixel coordinates so sprite positions
        # don't need to know about the physical pixel ratio.
        # Also override on_resize so dispatch_events() doesn't reset it.
        self.hidpi = self.window.get_pixel_ratio() != 1.0
        if self.hidpi:
            lw, lh = w * PIXELS_PER_UNIT, h * PIXELS_PER_UNIT
            logical_projection = pyglet.math.Mat4.orthogonal_projection(
                0, lw, 0, lh, -255, 255
            )
            self.window.projection = logical_projection

            def on_resize(_width, _height):
                self.window.projection = logical_projection

            self.window.push_handlers(on_resize)
        # batch needs be initialized after window

        batch = pyglet.graphics.Batch()
        c_sprites: dict[Counter, CounterSprite] = dict()
        p_sprites: dict[Player, PlayerSprite] = dict()
        f_sprites: list[FloorSprite] = []
        for x in range(w):
            for y in range(h):
                tile = game.kitchen[x][y]
                if tile == None:
                    f_sprites.append(FloorSprite(x, y, batch))
                elif type(tile) is Counter:
                    c_sprites[tile] = CounterSprite(
                        tile.describe_holding(), x, y, batch
                    )
        for player in game.players:
            p_sprites[player] = PlayerSprite(player.x, player.y, batch)
        self.c_sprites, self.p_sprites, self.f_sprites = c_sprites, p_sprites, f_sprites
        self.game, self.batch = game, batch

        self.clock = None
        self.keyboard_enabled = False
        self.is_closed = False
        self.keyboard_map = keyboard_map
        if keyboard_map is not None:
            self.setup_keyboard_handlers()
            self.keyboard_enabled = True
        self.window.on_close = self.close
        self.window.switch_to()
        self.draw()

    def draw(self):
        self.window.clear()
        self.batch.draw()
        self.window.flip()

    def close(self):
        if self.is_closed:
            return
        self.is_closed = True
        if self.keyboard_enabled:
            self.window.pop_handlers()
        if self.hidpi:
            self.window.pop_handlers()
        self.window.close()

    def refresh(self):
        if self.is_closed:
            return
        self.players_turn_and_interact()
        self.players_move()
        self.draw()

    def animate(self, speed: float = 5.0):
        if self.is_closed:
            return
        any_update = self.players_turn_and_interact()

        if any_update:
            self.draw()
            self.window.dispatch_events()
            time.sleep(0.1)
            if self.is_closed:
                return

        last_time = time.perf_counter()
        while True:
            now = time.perf_counter()
            dt = now - last_time
            last_time = now

            if self.players_moving(dt, speed):
                break

            self.window.dispatch_events()
            if self.is_closed:
                return
            self.draw()
            sleep_time = 1 / 90.0 - (time.perf_counter() - now)
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.draw()

    def wait_keyboard(self):
        while True:
            actions = self.read_keyboard()
            if self.is_closed or not all(a == Action.NOOP for a in actions.values()):
                return actions
            time.sleep(0.01)

    def read_keyboard(self):
        assert self.keyboard_enabled, "must pass in keyboard_map at initialization"
        actions = {p.id: Action.NOOP for p in self.game.players}
        if self.is_closed:
            return actions

        self.window.dispatch_events()
        for p_id in actions:
            if self.keyboard_map and p_id in self.keyboard_map:
                mapping = self.keyboard_map[p_id]
                for key, action in mapping.items():
                    if key in self.pressed and self.pressed[key]:
                        actions[p_id] = action
                    if key in self.triggered and self.triggered[key]:
                        self.triggered[key] = False
                        actions[p_id] = action
        return actions

    def setup_keyboard_handlers(self):
        self.pressed: dict[int, bool] = dict()
        self.triggered: dict[int, bool] = dict()
        for p in self.game.players:
            if p.id in self.keyboard_map:
                mapping = self.keyboard_map[p.id]
                for key, action in mapping.items():
                    if action == Action.INTERACT:
                        self.triggered[key] = False
                    else:
                        self.pressed[key] = False

        def on_key_press(symbol, modifiers):
            if symbol in self.pressed:
                self.pressed[symbol] = True
            elif symbol in self.triggered:
                self.triggered[symbol] = True

        def on_key_release(symbol, modifiers):
            if symbol in self.pressed:
                self.pressed[symbol] = False

        self.window.push_handlers(on_key_press, on_key_release)

    def players_turn_and_interact(self):
        any_update = False
        for player, sprite in self.p_sprites.items():
            holding, facing = player.describe_holding(), player.facing
            if holding != sprite.holding or facing != sprite.facing:
                sprite.update_image(holding, facing)
                any_update = True
        for counter, sprite in self.c_sprites.items():
            holding = counter.describe_holding()
            if holding != sprite.holding:
                sprite.update_image(holding)
                any_update = True
        return any_update

    def players_move(self):
        for player, sprite in self.p_sprites.items():
            sprite.update_position(player.x, player.y)

    def players_moving(self, dt: float, speed: float):
        # print('moving', dt)
        finished = True
        for player, sprite in self.p_sprites.items():
            x, y = sprite.x, sprite.y
            dx, dy = player.x - x, player.y - y
            if dx != 0:
                d_ = dt * speed
                if d_ > abs(dx):
                    x = player.x
                else:
                    finished = False
                    x += d_ if dx > 0 else -d_
                sprite.update_position(x=x)
            if dy != 0:
                d_ = dt * speed
                if d_ > abs(dy):
                    y = player.y
                else:
                    finished = False
                    y += d_ if dy > 0 else -d_
                sprite.update_position(y=y)
        return finished
