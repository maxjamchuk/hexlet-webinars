class PlainTrack:
    def __init__(self, artist: str, title: str, year: int):
        self.artist = artist
        self.title = title
        self.year = year


class SlottedTrack:
    __slots__ = ("artist", "title", "year")

    def __init__(self, artist: str, title: str, year: int):
        self.artist = artist
        self.title = title
        self.year = year
