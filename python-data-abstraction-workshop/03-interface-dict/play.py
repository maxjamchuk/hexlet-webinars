from fixtures import ROWS
from game import move, new_game, render
from world import make_world


def main():
    state = new_game(make_world(ROWS))
    print(render(state))
    while not state["won"]:
        try:
            command = input("Command (w/a/s/d, q): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nBYE")
            break
        if command == "q":
            print("BYE")
            break
        for message in move(state, command):
            print(message)
        print(render(state))


if __name__ == "__main__":
    main()
