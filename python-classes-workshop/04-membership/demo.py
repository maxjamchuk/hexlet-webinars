from fixtures import create_playlist, create_tracks
from models import Playlist, Track


def section(title):
    print(f"\n--- {title} ---")


def main():
    tracks = create_tracks()
    playlist = create_playlist()
    section("04: принадлежность по равенству Track")
    equal_copy = Track("The Cure", "A Forest", 1980)
    other = Track("The Cure", "Boys Don't Cry", 1979)
    print("tracks[1] in playlist:", tracks[1] in playlist)
    print("equal_copy in playlist:", equal_copy in playlist)
    print("other in playlist:", other in playlist)
    print('"A Forest" in playlist:', "A Forest" in playlist)
    print("other not in playlist:", other not in playlist)
    print("tracks[0] in empty:", tracks[0] in Playlist("Пустой", []))
    print("Поиск строки по названию был бы другим контрактом оператора in.")


if __name__ == '__main__':
    main()
