import unittest

from fixtures import ROWS
from game import get_tile, move, new_game, render


class GameTest(unittest.TestCase):
    def setUp(self):
        self.state = new_game(ROWS)

    def test_map_and_dimensions(self):
        self.assertEqual((len(ROWS[0]), len(ROWS)), (13, 6))
        self.assertEqual(get_tile(ROWS, 11, 4), "E")
        self.assertEqual(get_tile(ROWS, 1, 1), ".")

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
