from world import get_height, get_tile, get_width, is_exit, is_walkable


DIRECTIONS = {"w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0)}


def new_game(world):
    return {"world": world, "x": 1, "y": 1, "won": False, "has_key": False}


def move(state, command):
    if command not in DIRECTIONS:
        return [f"UNKNOWN COMMAND: {command}"]

    dx, dy = DIRECTIONS[command]
    x, y = state["x"] + dx, state["y"] + dy
    world = state["world"]
    if not is_walkable(world, x, y):
        return [f"MOVE {command}: blocked"]

    state["x"], state["y"] = x, y
    result = [f"MOVE {command}: ({x}, {y})"]
    if get_tile(world, x, y) == "K" and not state["has_key"]:
        state["has_key"] = True
        result.append("KEY COLLECTED")
    if is_exit(world, x, y):
        result.append("EXIT REACHED")
        if state["has_key"]:
            state["won"] = True
            result.append("WIN")
        else:
            result.append("EXIT LOCKED: key required")
    return result


def render(state):
    world = state["world"]
    lines = []
    for y in range(get_height(world)):
        line = ""
        for x in range(get_width(world)):
            tile = get_tile(world, x, y)
            if tile == "K" and state["has_key"]:
                tile = "."
            line += "@" if (x, y) == (state["x"], state["y"]) else tile
        lines.append(line)
    return "\n".join(lines)
