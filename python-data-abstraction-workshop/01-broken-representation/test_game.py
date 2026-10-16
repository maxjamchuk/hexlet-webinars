import unittest

from fixtures import WORLD
from game import get_tile, new_game, render


class BrokenRepresentationTest(unittest.TestCase):
    def test_cells_cover_whole_map(self):
        self.assertEqual(len(WORLD), 13 * 6)
        self.assertEqual(WORLD[(11, 4)], "E")

    def test_old_indexing_fails_with_key_error(self):
        with self.assertRaisesRegex(KeyError, "0"):
            get_tile(WORLD, 1, 0)
        with self.assertRaises(KeyError):
            render(new_game(WORLD))


if __name__ == "__main__":
    unittest.main()
