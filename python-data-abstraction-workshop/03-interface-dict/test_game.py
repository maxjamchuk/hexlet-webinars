import unittest

from fixtures import ROWS
from game import move, new_game, render
from world import get_height, get_tile, get_width, is_exit, is_walkable, make_world


class GameTest(unittest.TestCase):
    def setUp(self):
        self.world = make_world(ROWS)
        self.state = new_game(self.world)

    def test_public_world_contract(self):
        self.assertEqual((get_width(self.world), get_height(self.world)), (13, 6))
        self.assertEqual(get_tile(self.world, 11, 4), "E")
        self.assertEqual(get_tile(self.world, 1, 1), ".")
        self.assertTrue(is_exit(self.world, 11, 4))
        self.assertFalse(is_exit(self.world, -1, 4))
        self.assertTrue(is_walkable(self.world, 1, 1))
        self.assertFalse(is_walkable(self.world, 0, 0))
        for x, y in ((-1, 1), (1, -1), (13, 1), (1, 6)):
            with self.subTest(point=(x, y)):
                with self.assertRaisesRegex(IndexError, "^coordinates out of bounds$"):
                    get_tile(self.world, x, y)
                self.assertFalse(is_walkable(self.world, x, y))
                self.assertFalse(is_exit(self.world, x, y))

    def test_four_directions_and_walls(self):
        self.assertEqual(move(self.state, "w"), ["MOVE w: blocked"])
        self.assertEqual(move(self.state, "a"), ["MOVE a: blocked"])
        for command, point in (("d", (2, 1)), ("s", (2, 2)),
                               ("a", (1, 2)), ("w", (1, 1))):
            move(self.state, command)
            self.assertEqual((self.state["x"], self.state["y"]), point)

    def test_boundary_and_unknown_command(self):
        self.state["x"] = 0
        self.assertEqual(move(self.state, "a"), ["MOVE a: blocked"])
        self.assertEqual(move(self.state, "?"), ["UNKNOWN COMMAND: ?"])

    def test_exit_and_render(self):
        expected = "\n".join(("#############", "#@....#.....#", *ROWS[2:]))
        self.assertEqual(render(self.state), expected)
        commands = ["s"] * 2 + ["d"] * 10 + ["s"]
        events = [event for command in commands for event in move(self.state, command)]
        self.assertEqual(events[-2:], ["EXIT REACHED", "WIN"])
        self.assertTrue(self.state["won"])
        self.assertIn("#..##......@#", render(self.state))


if __name__ == "__main__":
    unittest.main()
