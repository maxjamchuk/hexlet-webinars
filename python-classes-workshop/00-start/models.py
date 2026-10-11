class Track:
    def __init__(self, artist: str, title: str, year: int):
        self.artist = artist
        self.title = title
        self.year = year


class Playlist:
    def __init__(self, name: str, tracks):
        self.name = name
        self._tracks = list(tracks)
