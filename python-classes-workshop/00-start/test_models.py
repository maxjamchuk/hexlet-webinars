import unittest

from fixtures import create_playlist, create_tracks
from models import Playlist, Track


class ModelsTest(unittest.TestCase):
    def test_track_attributes(self):
        track = Track("The Cure", "A Forest", 1980)
        self.assertEqual((track.artist, track.title, track.year),
                         ("The Cure", "A Forest", 1980))

    def test_playlist_name_and_order(self):
        playlist = create_playlist()
        self.assertEqual(playlist.name, "Post-Punk 80s")
        self.assertEqual(
            [(track.artist, track.title, track.year) for track in playlist._tracks],
            [("Joy Division", "Love Will Tear Us Apart", 1980),
             ("The Cure", "A Forest", 1980),
             ("Siouxsie and the Banshees", "Spellbound", 1981),
             ("The Sound", "Winning", 1981),
             ("The Chameleons", "Second Skin", 1983),
             ("Bauhaus", "She's in Parties", 1983)],
        )

    def test_playlist_copies_input(self):
        source = create_tracks()
        playlist = Playlist("Copy", source)
        source.clear()
        self.assertEqual(len(playlist._tracks), 6)
        self.assertIsNot(playlist._tracks, source)

    def test_fixtures_create_fresh_objects(self):
        self.assertIsNot(create_tracks()[0], create_tracks()[0])
        self.assertIsNot(create_playlist(), create_playlist())

    def test_length_unavailable(self):
        with self.assertRaises(TypeError):
            len(create_playlist())

    def test_iteration_unavailable(self):
        with self.assertRaises(TypeError):
            iter(create_playlist())


if __name__ == '__main__':
    unittest.main()
