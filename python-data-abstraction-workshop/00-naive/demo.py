from fixtures import ROWS
from game import move, new_game, render


def main():
    state = new_game(ROWS)
    print("START: (1, 1)")
    print(render(state))
    commands = ["a"] + ["s"] * 2 + ["d"] * 10 + ["s"]
    for command in commands:
        for message in move(state, command):
            print(message)
    print(render(state))


if __name__ == "__main__":
    main()
