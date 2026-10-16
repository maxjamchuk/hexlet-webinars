from fixtures import ROWS
from game import move, new_game, render
from world import make_world


def main():
    state = new_game(make_world(ROWS))
    print("START: (1, 1)")
    print(render(state))
    commands = ["a"] + ["s"] * 2 + ["d"] * 10 + ["s"]
    for command in commands:
        for message in move(state, command):
            print(message)
    print(render(state))
    examples = ((), ("E.", "#"), ("EX",), ("..",), ("EE",))
    for rows in examples:
        try:
            make_world(rows)
        except ValueError as error:
            print(f"EXPECTED INVALID MAP: {error}")


if __name__ == "__main__":
    main()
