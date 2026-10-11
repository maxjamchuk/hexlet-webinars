from fixtures import create_playlist, create_tracks
from models import Playlist, Track


def section(title):
    print(f"\n--- {title} ---")


def main():
    tracks = create_tracks()
    playlist = create_playlist()
    section("02: идентичность и равенство")
    first = Track("The Cure", "A Forest", 1980)
    second = Track("The Cure", "A Forest", 1980)
    print("first is second:", first is second)
    print("first == second:", first == second)
    print("first == tracks[0]:", first == tracks[0])
    print('first == "A Forest":', first == "A Forest")
    print('first.__eq__("A Forest") is NotImplemented:',
          first.__eq__("A Forest") is NotImplemented)
    print("NotImplemented предлагает Python попробовать другую сторону сравнения;")
    print("NotImplementedError — исключение для нереализованной операции.")
    try:
        hash(first)
    except TypeError as error:
        print(f"TypeError: {error}. Собственный __eq__ сделал Track нехешируемым.")


if __name__ == '__main__':
    main()
