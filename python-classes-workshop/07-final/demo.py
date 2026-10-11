from fixtures import create_playlist, create_tracks
from models import Playlist, Track


def section(title):
    print(f"\n--- {title} ---")


def main():
    tracks = create_tracks()
    playlist = create_playlist()
    section("07: Track")
    track = tracks[1]
    print("print(track):", track)
    print("repr(track):", repr(track))
    print("track == равная копия:", track == Track("The Cure", "A Forest", 1980))

    section("07: Playlist")
    print("print(playlist):", playlist)
    print("repr(playlist):", repr(playlist))
    print("len(playlist):", len(playlist))
    print("bool(playlist):", bool(playlist))
    print("равная копия in playlist:", Track("The Cure", "A Forest", 1980) in playlist)
    print("playlist[0]:", playlist[0])
    print("playlist[-1]:", playlist[-1])
    print("playlist[1:3]:", playlist[1:3])
    for item in playlist:
        print("for:", item)
    iterator = iter(playlist)
    print("next(iter(playlist)):", next(iterator))
    print("Методы имеют смысл там, где операция естественна для объекта.")


if __name__ == '__main__':
    main()
