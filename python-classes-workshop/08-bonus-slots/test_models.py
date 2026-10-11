import unittest

from models import PlainTrack, SlottedTrack


class SlotsTest(unittest.TestCase):
    def test_plain_instance_dictionary_and_new_attribute(self):
        track = PlainTrack("The Cure", "A Forest", 1980)
        self.assertEqual(track.__dict__, {
            "artist": "The Cure", "title": "A Forest", "year": 1980
        })
        track.note = "post-punk"
        self.assertEqual(track.note, "post-punk")

    def test_slots_and_readable_attributes(self):
        track = SlottedTrack("The Cure", "A Forest", 1980)
        self.assertEqual(SlottedTrack.__slots__, ("artist", "title", "year"))
        self.assertEqual((track.artist, track.title, track.year),
                         ("The Cure", "A Forest", 1980))
        with self.assertRaises(AttributeError):
            _ = track.__dict__

    def test_declared_attributes_are_mutable(self):
        track = SlottedTrack("The Cure", "A Forest", 1980)
        track.year = 1981
        self.assertEqual(track.year, 1981)

    def test_new_attribute_is_rejected(self):
        track = SlottedTrack("The Cure", "A Forest", 1980)
        with self.assertRaises(AttributeError):
            track.note = "post-punk"


if __name__ == "__main__":
    unittest.main()
