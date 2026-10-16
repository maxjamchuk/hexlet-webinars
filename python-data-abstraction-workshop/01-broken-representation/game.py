DIRECTIONS = {"w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0)}


def new_game(world):
    return {"world": world, "x": 1, "y": 1, "won": False}


def get_tile(world, x, y):
    return world[y][x]


def move(state, command):
    if command not in DIRECTIONS:
        return [f"UNKNOWN COMMAND: {command}"]

    dx, dy = DIRECTIONS[command]
    x, y = state["x"] + dx, state["y"] + dy
    world = state["world"]
    if not (0 <= y < len(world) and 0 <= x < len(world[0])):
        return [f"MOVE {command}: blocked"]
    if get_tile(world, x, y) == "#":
        return [f"MOVE {command}: blocked"]

    state["x"], state["y"] = x, y
    result = [f"MOVE {command}: ({x}, {y})"]
    if get_tile(world, x, y) == "E":
        state["won"] = True
        result.extend(("EXIT REACHED", "WIN"))
    return result


def render(state):
    world = state["world"]
    lines = []
    for y in range(len(world)):
        line = ""
        for x in range(len(world[0])):
            line += "@" if (x, y) == (state["x"], state["y"]) else get_tile(world, x, y)
        lines.append(line)
    return "\n".join(lines)
