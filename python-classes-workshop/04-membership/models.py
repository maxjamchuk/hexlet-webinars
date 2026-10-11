class Track:
    def __init__(self, artist: str, title: str, year: int):
        self.artist = artist
        self.title = title
        self.year = year

    def __str__(self):
        return f"{self.artist} — {self.title} ({self.year})"

    def __repr__(self):
        return (
            f"Track(artist={self.artist!r}, title={self.title!r}, "
            f"year={self.year!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, Track):
            return NotImplemented
        return (self.artist, self.title, self.year) == (
            other.artist, other.title, other.year
        )


class Playlist:
    def __init__(self, name: str, tracks):
        self.name = name
        self._tracks = list(tracks)

    def __str__(self):
        return f"{self.name} — треков: {len(self)}"

    def __repr__(self):
        return f"Playlist(name={self.name!r}, tracks={self._tracks!r})"

    def __len__(self):
        return len(self._tracks)

    def __contains__(self, track):
        return track in self._tracks
