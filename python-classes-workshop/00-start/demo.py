from fixtures import create_playlist, create_tracks
from models import Playlist, Track


def section(title):
    print(f"\n--- {title} ---")


def main():
    tracks = create_tracks()
    playlist = create_playlist()
    section("00: обычные классы")
    track = Track("The Cure", "A Forest", 1980)
    print("print(track):", track)
    print("print(playlist):", playlist)
    print("Пока видим стандартное представление экземпляров.")
    print("Адрес меняется при каждом запуске.")

    section("Операции пока недоступны")
    try:
        print("len(playlist):", len(playlist))
    except TypeError as error:
        print(f"TypeError: {error}. У Playlist пока нет протокола длины.")
    try:
        for item in playlist:
            print(item)
    except TypeError as error:
        print(f"TypeError: {error}. У Playlist пока нет протокола перебора.")
    print("У обычного списка эти операции уже есть. Как научить им наш класс?")


if __name__ == '__main__':
    main()
