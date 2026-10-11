from fixtures import create_playlist, create_tracks
from models import Playlist, Track


def section(title):
    print(f"\n--- {title} ---")


def main():
    tracks = create_tracks()
    playlist = create_playlist()
    section("03: длина и истинность")
    empty = Playlist("Пустой", [])
    print("len(playlist):", len(playlist))
    print("len(empty):", len(empty))
    print("bool(playlist):", bool(playlist))
    print("bool(empty):", bool(empty))
    if playlist:
        print("if playlist: коллекция не пуста")
    if not empty:
        print("if not empty: коллекция пуста")
    print("__bool__ не нужен: Python использует длину. У отдельного Track длины нет.")

    class BrokenLength:
        def __len__(self):
            return -1

    try:
        len(BrokenLength())
    except ValueError as error:
        print(f"ValueError: {error}. Длина должна быть неотрицательной.")


if __name__ == '__main__':
    main()
