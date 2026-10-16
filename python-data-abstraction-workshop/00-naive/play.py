from fixtures import ROWS
from game import move, new_game, render


def main():
    state = new_game(ROWS)
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
