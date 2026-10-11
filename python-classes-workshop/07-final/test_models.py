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

    def test_track_str_and_repr(self):
        track = Track("The Cure", "A Forest", 1980)
        self.assertEqual(str(track), "The Cure — A Forest (1980)")
        self.assertEqual(repr(track),
                         "Track(artist='The Cure', title='A Forest', year=1980)")
        self.assertEqual(str([track]), f"[{repr(track)}]")

    def test_playlist_str_and_repr(self):
        playlist = create_playlist()
        self.assertEqual(str(playlist), "Post-Punk 80s — треков: 6")
        shown = repr(playlist)
        self.assertIn("Playlist(name='Post-Punk 80s'", shown)
        self.assertIn("Track(artist='The Cure', title='A Forest', year=1980)", shown)

    def test_empty_and_escaped_repr(self):
        self.assertEqual(str(Playlist("Empty", [])), "Empty — треков: 0")
        self.assertIn("tracks=[]", repr(Playlist("Empty", [])))
        track = Track("O'Neil", "Line\nBreak", 1980)
        self.assertIn(repr("O'Neil"), repr(track))
        self.assertIn(repr("Line\nBreak"), repr(track))
        self.assertIn(repr("Mix\nName"), repr(Playlist("Mix\nName", [track])))

    def test_equal_value_different_identity(self):
        first = Track("The Cure", "A Forest", 1980)
        second = Track("The Cure", "A Forest", 1980)
        self.assertIsNot(first, second)
        self.assertEqual(first, second)
        self.assertEqual(first, first)

    def test_each_field_changes_equality(self):
        original = Track("The Cure", "A Forest", 1980)
        for changed in (Track("Bauhaus", "A Forest", 1980),
                        Track("The Cure", "Other", 1980),
                        Track("The Cure", "A Forest", 1981)):
            with self.subTest(changed=repr(changed)):
                self.assertNotEqual(original, changed)

    def test_incompatible_type_and_hash(self):
        track = create_tracks()[0]
        self.assertFalse(track == "Love Will Tear Us Apart")
        self.assertIs(track.__eq__("Love Will Tear Us Apart"), NotImplemented)
        with self.assertRaises(TypeError):
            hash(track)

    def test_compatible_subclass(self):
        class SpecialTrack(Track):
            pass

        self.assertEqual(Track("The Cure", "A Forest", 1980),
                         SpecialTrack("The Cure", "A Forest", 1980))

    def test_len_and_bool(self):
        playlist = create_playlist()
        empty = Playlist("Empty", [])
        self.assertEqual(len(playlist), 6)
        self.assertEqual(len(empty), 0)
        self.assertTrue(playlist)
        self.assertFalse(empty)
        self.assertEqual(str(playlist), "Post-Punk 80s — треков: 6")
        self.assertNotIn("__bool__", Playlist.__dict__)

    def test_track_has_no_length(self):
        with self.assertRaises(TypeError):
            len(create_tracks()[0])

    def test_membership_by_track_equality(self):
        tracks = create_tracks()
        playlist = Playlist("Mix", tracks)
        self.assertIn(tracks[1], playlist)
        self.assertIn(Track("The Cure", "A Forest", 1980), playlist)
        self.assertNotIn(Track("The Cure", "Other", 1980), playlist)
        self.assertNotIn("A Forest", playlist)
        self.assertNotIn(tracks[0], Playlist("Empty", []))
        self.assertTrue(Track("The Cure", "Other", 1980) not in playlist)

    def test_explicit_iterator_and_repeated_iteration(self):
        playlist = create_playlist()
        self.assertIn("__iter__", Playlist.__dict__)
        iterator = iter(playlist)
        self.assertIs(iter(iterator), iterator)
        self.assertEqual(next(iterator).title, "Love Will Tear Us Apart")
        self.assertEqual(next(iterator).title, "A Forest")
        self.assertEqual([track.title for track in playlist],
                         [track.title for track in create_tracks()])
        self.assertEqual(list(playlist), list(playlist))
        self.assertEqual(list(Playlist("Empty", [])), [])
        list(iterator)
        with self.assertRaises(StopIteration):
            next(iterator)

    def test_iter_must_return_iterator(self):
        class BrokenIterable:
            def __iter__(self):
                return create_tracks()

        with self.assertRaises(TypeError):
            iter(BrokenIterable())

    def test_indexing_still_works(self):
        playlist = create_playlist()
        self.assertEqual(playlist[0].title, "Love Will Tear Us Apart")
        self.assertIsInstance(playlist[1:3], list)

    def test_full_public_interface(self):
        playlist = create_playlist()
        track = Track("The Cure", "A Forest", 1980)
        self.assertIn(str(track), str(playlist[1]))
        self.assertIn(repr(track), repr(playlist))
        self.assertIn(track, playlist)
        self.assertEqual(len(playlist), len(list(playlist)))
        self.assertTrue(bool(playlist))
        self.assertEqual(next(iter(playlist)), playlist[0])
        self.assertEqual(playlist[1:3], list(playlist)[1:3])


if __name__ == '__main__':
    unittest.main()
