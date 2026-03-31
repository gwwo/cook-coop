import numpy as np

import pathlib

ITEM_RAW_PIXELS = 5


def load(file_name):
    with open(pathlib.Path(__file__).parent / (file_name + ".txt"), "r") as f:
        lines = [ls for l in f if (ls := l.strip("\n"))]
    assert len(lines) == ITEM_RAW_PIXELS
    assert all(len(l) == ITEM_RAW_PIXELS * 2 for l in lines)
    pixels = np.zeros((ITEM_RAW_PIXELS, ITEM_RAW_PIXELS), np.float32)
    for row, l in enumerate(lines):
        for col in range(ITEM_RAW_PIXELS):
            square = l[col * 2 : col * 2 + 2]
            if square == "██":
                pixels[row, col] = 1.0
            else:
                assert square == "  "
    return pixels


PIXELS = dict()

PIXELS["counter"] = {
    "empty": load("empty_counter"),
    "tomato_dispenser": load("tomato_dispenser_counter"),
    "tomato": load("tomato_on_counter"),
    "server": load("server_counter"),
    "plate_dispenser": load("plate_dispenser_counter"),
    "plate": load("plate_on_counter"),
    "soup": load("soup_on_counter"),
    "pot": load("pot_counter"),
    "pot_with_1_cooking": load("pot_counter_with_1_tomato"),
    "pot_with_2_cooking": load("pot_counter_with_2_tomato"),
    "pot_ready": load("pot_counter_with_soup"),
}


def rotate(pixels):
    return {
        "south": pixels,
        "north": np.flip(pixels, 0),
        "east": np.transpose(pixels),
        "west": np.flip(np.transpose(pixels), 1),
    }


PIXELS["chef"] = {
    "empty": rotate(load("chef")),
    "plate": rotate(load("chef_with_plate")),
    "soup": rotate(load("chef_with_soup")),
    "tomato": rotate(load("chef_with_tomato")),
}
