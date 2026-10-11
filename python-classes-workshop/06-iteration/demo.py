from fixtures import create_playlist, create_tracks
from models import Playlist, Track


def section(title):
    print(f"\n--- {title} ---")


def main():
    tracks = create_tracks()
    playlist = create_playlist()
    section("06: явный протокол итерации")
    iterator = iter(playlist)
    print("iter(playlist) is playlist:", iterator is playlist)
    print("iter(iterator) is iterator:", iter(iterator) is iterator)
    print("next(iterator):", next(iterator))
    print("next(iterator):", next(iterator))
    for track in playlist:
        print("for:", track)
    for _ in iterator:
        pass
    try:
        next(iterator)
    except StopIteration:
        print("StopIteration: итератор исчерпан; новый iter(playlist) начнёт сначала.")

    section("Неправильный __iter__")
    class BrokenIterable:
        def __iter__(self):
            return tracks

    try:
        iter(BrokenIterable())
    except TypeError as error:
        print(f"TypeError: {error}. __iter__ должен вернуть итератор, а не список.")


if __name__ == '__main__':
    main()
