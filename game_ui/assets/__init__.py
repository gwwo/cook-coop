import pyglet
import pathlib

ITEM_RAW_PIXELS = 15

IMAGE = dict()


def load(img_file: str):
    img = pyglet.image.load(pathlib.Path(__file__).parent / img_file)
    MARGIN_PIXELS = 1

    def _item(left: int, bottom: int = 1):
        return img.get_region(
            MARGIN_PIXELS + (left - 1) * (ITEM_RAW_PIXELS + 2 * MARGIN_PIXELS),
            MARGIN_PIXELS + (bottom - 1) * (ITEM_RAW_PIXELS + 2 * MARGIN_PIXELS),
            width=ITEM_RAW_PIXELS,
            height=ITEM_RAW_PIXELS,
        )

    return _item


item = load("terrain.png")

IMAGE["empty_counter"] = item(1)
IMAGE["plate_dispenser_counter"] = item(2)
IMAGE["floor"] = item(3)
IMAGE["tomato_dispenser_counter"] = item(7)
IMAGE["pot_counter"] = item(5)
IMAGE["server_counter"] = item(6)


item = load("chefs.png")


IMAGE["chef_empty_hand"] = {
    "south": item(5, 4),
    "north": item(6, 6),
    "west": item(4, 2),
    "east": item(1, 7),
}
IMAGE["chef_with_plate"] = {
    "south": item(1, 3),
    "north": item(2, 5),
    "west": item(6, 2),
    "east": item(3, 7),
}
IMAGE["chef_with_tomato"] = {
    "south": item(3, 2),
    "north": item(4, 4),
    "west": item(2, 1),
    "east": item(5, 6),
}
IMAGE["chef_with_tomato_soup"] = {
    "south": item(2, 2),
    "north": item(3, 4),
    "west": item(1, 1),
    "east": item(4, 6),
}


item = load("objects.png")

IMAGE["plate"] = item(1)
IMAGE["tomato"] = item(15)
IMAGE["pot_with_1_tomato"] = item(9)
IMAGE["pot_with_2_tomato"] = item(10)
IMAGE["pot_with_3_tomato"] = item(11)
IMAGE["pot_with_tomato_soup"] = item(13)
IMAGE["tomato_soup"] = item(14)
