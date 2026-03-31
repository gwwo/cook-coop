import pyglet
from pyglet import gl
from typing import Union
from .assets import IMAGE, ITEM_RAW_PIXELS

# how many pixels in the game's measurement of 1
PIXELS_PER_UNIT = 60


class PixelSprite(pyglet.sprite.Sprite):
    def __init__(self, img, x: float, y: float, batch):
        super().__init__(
            img, int(x * PIXELS_PER_UNIT), int(y * PIXELS_PER_UNIT), batch=batch
        )
        self.scale = PIXELS_PER_UNIT / ITEM_RAW_PIXELS
        self._pixelate()

    def _pixelate(self):
        gl.glTexParameteri(
            self._texture.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST
        )
        gl.glTexParameteri(
            self._texture.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST
        )

    def set_image(self, img):
        self.image = img
        self._pixelate()

    def set_position(self, x: Union[float, None] = None, y: Union[float, None] = None):
        if x != None:
            self.x = int(x * PIXELS_PER_UNIT)
        if y != None:
            self.y = int(y * PIXELS_PER_UNIT)


class FloorSprite:
    def __init__(self, x, y, batch):
        self.raw = PixelSprite(IMAGE["floor"], x, y, batch)


class PlayerSprite:
    def __init__(self, x: float, y: float, batch):
        self.raw = PixelSprite(IMAGE["chef_empty_hand"]["south"], x, y, batch)
        self.x, self.y = x, y
        self.holding = "empty"
        self.facing = "south"

    def update_image(self, holding: str, facing: str):
        mapping = {
            "empty": "chef_empty_hand",
            "plate": "chef_with_plate",
            "soup": "chef_with_tomato_soup",
            "tomato": "chef_with_tomato",
        }
        label = mapping[holding]
        self.raw.set_image(IMAGE[label][facing])
        self.holding, self.facing = holding, facing

    def update_position(
        self, x: Union[float, None] = None, y: Union[float, None] = None
    ):
        if x != None:
            self.raw.set_position(x=x)
            self.x = x
        if y != None:
            self.raw.set_position(y=y)
            self.y = y


class CounterSprite:
    def __init__(self, holding: str, x, y, batch):
        mapping = {
            "empty": "empty_counter",
            "pot": "pot_counter",
            "tomato_dispenser": "tomato_dispenser_counter",
            "plate_dispenser": "plate_dispenser_counter",
            "server": "server_counter",
        }
        label = mapping[holding]
        self.raw = PixelSprite(IMAGE[label], x, y, batch)
        self.holding = holding
        self.overlay = PixelSprite(IMAGE[label], x, y, batch)
        self.overlay.visible = False

    def update_image(self, holding: str):
        mapping = {
            "tomato": "tomato",
            "plate": "plate",
            "soup": "tomato_soup",
            "pot_with_1_cooking": "pot_with_1_tomato",
            "pot_with_2_cooking": "pot_with_2_tomato",
            "pot_with_3_cooking": "pot_with_3_tomato",
            "pot_ready": "pot_with_tomato_soup",
        }
        if holding in mapping:
            label = mapping[holding]
            self.overlay.set_image(IMAGE[label])
            self.overlay.visible = True
        else:
            self.overlay.visible = False
        self.holding = holding
