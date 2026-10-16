def make_world(rows):
    return tuple(rows)


def get_width(world):
    return len(world[0])


def get_height(world):
    return len(world)


def _in_bounds(world, x, y):
    return 0 <= x < get_width(world) and 0 <= y < get_height(world)


def get_tile(world, x, y):
    if not _in_bounds(world, x, y):
        raise IndexError("coordinates out of bounds")
    return world[y][x]


def is_walkable(world, x, y):
    return _in_bounds(world, x, y) and get_tile(world, x, y) != "#"


def is_exit(world, x, y):
    return _in_bounds(world, x, y) and get_tile(world, x, y) == "E"
