import copy
import unittest

from fixtures import ROWS
from game import move, new_game, render
from world import get_height, get_tile, get_width, is_exit, is_walkable, make_world


class KeyGameTest(unittest.TestCase):
    def setUp(self):
        self.world = make_world(ROWS)
        self.state = new_game(self.world)

    def test_public_world_contract(self):
        self.assertEqual((get_width(self.world), get_height(self.world)), (13, 6))
        self.assertEqual(get_tile(self.world, 4, 3), "K")
        self.assertEqual(get_tile(self.world, 11, 4), "E")
        self.assertTrue(is_walkable(self.world, 4, 3))
        self.assertTrue(is_exit(self.world, 11, 4))
        self.assertFalse(is_exit(self.world, -1, 4))
        self.assertFalse(is_walkable(self.world, 0, 0))
        for x, y in ((-1, 1), (1, -1), (13, 1), (1, 6)):
            with self.subTest(point=(x, y)):
                with self.assertRaisesRegex(IndexError, "^coordinates out of bounds$"):
                    get_tile(self.world, x, y)
                self.assertFalse(is_walkable(self.world, x, y))
                self.assertFalse(is_exit(self.world, x, y))

    def test_four_directions_walls_and_boundary(self):
        self.assertEqual(move(self.state, "w"), ["MOVE w: blocked"])
        self.assertEqual(move(self.state, "a"), ["MOVE a: blocked"])
        for command, point in (("d", (2, 1)), ("s", (2, 2)),
                               ("a", (1, 2)), ("w", (1, 1))):
            move(self.state, command)
            self.assertEqual((self.state["x"], self.state["y"]), point)
        self.state["x"] = 0
        self.assertEqual(move(self.state, "a"), ["MOVE a: blocked"])
        self.assertEqual(move(self.state, "?"), ["UNKNOWN COMMAND: ?"])

    def test_exit_without_key_and_leaving_it(self):
        commands = ["d"] * 4 + ["s"] * 2 + ["d"] * 6 + ["s"]
        events = [event for command in commands for event in move(self.state, command)]
        self.assertEqual(events[-2:], ["EXIT REACHED", "EXIT LOCKED: key required"])
        self.assertFalse(self.state["won"])
        self.assertFalse(self.state["has_key"])
        self.assertIn("#..##......@#", render(self.state))
        move(self.state, "w")
        self.assertEqual((self.state["x"], self.state["y"]), (11, 3))

    def test_key_persists_and_win_does_not_mutate_map(self):
        original = copy.deepcopy(self.world)
        events = []
        for command in ["s"] * 2 + ["d"] * 3:
            events.extend(move(self.state, command))
        self.assertEqual(events.count("KEY COLLECTED"), 1)
        self.assertTrue(self.state["has_key"])
        self.assertEqual(get_tile(self.world, 4, 3), "K")
        self.assertNotIn("K", render(self.state))
        move(self.state, "a")
        self.assertNotIn("KEY COLLECTED", move(self.state, "d"))
        self.assertTrue(self.state["has_key"])
        for command in ["d"] * 7 + ["s"]:
            events.extend(move(self.state, command))
        self.assertEqual(events[-2:], ["EXIT REACHED", "WIN"])
        self.assertTrue(self.state["won"])
        self.assertEqual(self.world, original)

    def test_exactly_one_key(self):
        for rows in (("E.",), ("EKK",)):
            with self.subTest(rows=rows):
                with self.assertRaisesRegex(ValueError, "^expected exactly one key$"):
                    make_world(rows)
        with self.assertRaisesRegex(ValueError, "^expected exactly one exit$"):
            make_world(("K.",))
        with self.assertRaisesRegex(ValueError, "^unsupported tile: X$"):
            make_world(("EKX",))


if __name__ == "__main__":
    unittest.main()
