def make_world(rows):
    rows = tuple(rows)
    cells = {}
    for y, row in enumerate(rows):
        for x, tile in enumerate(row):
            cells[(x, y)] = tile
    return {"width": len(rows[0]), "height": len(rows), "cells": cells}


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
