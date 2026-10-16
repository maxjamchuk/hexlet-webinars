def make_world(rows):
    rows = tuple(rows)
    if not rows:
        raise ValueError("map must not be empty")
    width = len(rows[0])
    if width == 0 or any(len(row) != width for row in rows):
        raise ValueError("rows must have equal non-zero width")

    cells = {}
    exit_count = 0
    key_count = 0
    for y, row in enumerate(rows):
        for x, tile in enumerate(row):
            if tile not in {"#", ".", "E", "K"}:
                raise ValueError(f"unsupported tile: {tile}")
            exit_count += tile == "E"
            key_count += tile == "K"
            cells[(x, y)] = tile
    if exit_count != 1:
        raise ValueError("expected exactly one exit")
    if key_count != 1:
        raise ValueError("expected exactly one key")
    return {"width": width, "height": len(rows), "cells": cells}


def get_width(world):
    return world["width"]


def get_height(world):
    return world["height"]


def _in_bounds(world, x, y):
    return 0 <= x < get_width(world) and 0 <= y < get_height(world)


def get_tile(world, x, y):
    if not _in_bounds(world, x, y):
        raise IndexError("coordinates out of bounds")
    return world["cells"][(x, y)]


def is_walkable(world, x, y):
    return _in_bounds(world, x, y) and get_tile(world, x, y) != "#"


def is_exit(world, x, y):
    return _in_bounds(world, x, y) and get_tile(world, x, y) == "E"
