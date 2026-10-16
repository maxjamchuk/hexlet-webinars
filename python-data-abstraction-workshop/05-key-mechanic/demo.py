from fixtures import ROWS
from game import move, new_game, render
from world import make_world


def run_route(name, commands):
    state = new_game(make_world(ROWS))
    print(f"ROUTE {name}")
    print("START: (1, 1)")
    for command in commands:
        for message in move(state, command):
            print(message)
    print(render(state))


def main():
    without_key = ["d"] * 4 + ["s"] * 2 + ["d"] * 6 + ["s"]
    with_key = ["a"] + ["s"] * 2 + ["d"] * 10 + ["s"]
    run_route("A: without key", without_key)
    run_route("B: with key", with_key)


if __name__ == "__main__":
    main()
