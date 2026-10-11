from models import Playlist, Track


def create_tracks():
    return [
        Track("Joy Division", "Love Will Tear Us Apart", 1980),
        Track("The Cure", "A Forest", 1980),
        Track("Siouxsie and the Banshees", "Spellbound", 1981),
        Track("The Sound", "Winning", 1981),
        Track("The Chameleons", "Second Skin", 1983),
        Track("Bauhaus", "She's in Parties", 1983),
    ]


def create_playlist():
    return Playlist("Post-Punk 80s", create_tracks())
