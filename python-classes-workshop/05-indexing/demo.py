from fixtures import create_playlist, create_tracks
from models import Playlist, Track


def section(title):
    print(f"\n--- {title} ---")


def main():
    tracks = create_tracks()
    playlist = create_playlist()
    section("05: индексы и срезы")
    print("playlist[0]:", playlist[0])
    print("playlist[-1]:", playlist[-1])
    print("playlist[1:3]:", playlist[1:3])
    print("type(playlist[1:3]):", type(playlist[1:3]).__name__)
    try:
        playlist[100]
    except IndexError as error:
        print(f"IndexError: {error}. Индекс вышел за границы.")

    section("Сюрприз: цикл работает без __iter__")
    print("'__iter__' in Playlist.__dict__:", "__iter__" in Playlist.__dict__)
    for track in playlist:
        print(track)
    print("Python запрашивает индексы 0, 1, ... до IndexError.")


if __name__ == '__main__':
    main()
