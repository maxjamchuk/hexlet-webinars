from fixtures import create_playlist, create_tracks
from models import Playlist, Track


def section(title):
    print(f"\n--- {title} ---")


def main():
    tracks = create_tracks()
    playlist = create_playlist()
    section("01: строка для человека")
    track = tracks[1]
    print("print(track):", track)
    print("str(track):", str(track))
    print('f"{track}":', f"{track}")
    print("print(playlist):", playlist)

    section("Представление для разработчика")
    print("repr(track):", repr(track))
    print("print([track]):", [track])
    print("repr(playlist):", repr(playlist))
    print("Список показывает repr() своих элементов, поэтому видны имена полей.")
    print("Восстановимость из repr() полезна, когда практична, но не гарантирована.")


if __name__ == '__main__':
    main()
