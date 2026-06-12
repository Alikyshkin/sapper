"""Тесты логики сапёра: python3 -m unittest"""

import unittest

from main import BOMB, create_field, neighbors, open_cell, parse_move


class TestNeighbors(unittest.TestCase):
    def test_corner_has_three_neighbors(self):
        self.assertEqual(set(neighbors(0, 0, 8, 8)), {(1, 0), (0, 1), (1, 1)})

    def test_edge_has_five_neighbors(self):
        self.assertEqual(len(list(neighbors(3, 0, 8, 8))), 5)

    def test_center_has_eight_neighbors(self):
        self.assertEqual(len(list(neighbors(4, 4, 8, 8))), 8)


class TestCreateField(unittest.TestCase):
    def test_bomb_count(self):
        field = create_field(8, 8, 9, 0, 0)
        bombs = sum(row.count(BOMB) for row in field)
        self.assertEqual(bombs, 9)

    def test_first_click_zone_is_safe(self):
        for _ in range(50):
            field = create_field(8, 8, 9, 4, 4)
            self.assertNotEqual(field[4][4], BOMB)
            for nx, ny in neighbors(4, 4, 8, 8):
                self.assertNotEqual(field[ny][nx], BOMB)
            # клетка без бомб-соседей должна быть нулём
            self.assertEqual(field[4][4], 0)

    def test_numbers_match_adjacent_bombs(self):
        field = create_field(10, 10, 15, 0, 0)
        for y in range(10):
            for x in range(10):
                if field[y][x] == BOMB:
                    continue
                expected = sum(
                    1 for nx, ny in neighbors(x, y, 10, 10) if field[ny][nx] == BOMB
                )
                self.assertEqual(field[y][x], expected, f"клетка ({x}, {y})")


class TestOpenCell(unittest.TestCase):
    def test_flood_fill_opens_empty_region(self):
        # Поле 4x4 без бомб: одно открытие раскрывает всё
        field = [[0] * 4 for _ in range(4)]
        opened, flags = set(), set()
        open_cell(field, opened, flags, 0, 0)
        self.assertEqual(len(opened), 16)

    def test_number_cell_opens_only_itself(self):
        field = [
            [1, 1, 0],
            [BOMB, 1, 0],
            [1, 1, 0],
        ]
        opened, flags = set(), set()
        open_cell(field, opened, flags, 1, 1)
        self.assertEqual(opened, {(1, 1)})

    def test_flood_fill_respects_flags(self):
        field = [[0] * 3 for _ in range(3)]
        opened, flags = set(), {(2, 2)}
        open_cell(field, opened, flags, 0, 0)
        self.assertNotIn((2, 2), opened)
        self.assertEqual(len(opened), 8)


class TestParseMove(unittest.TestCase):
    def test_open(self):
        self.assertEqual(parse_move("3 5", 8, 8), ("open", 3, 5))

    def test_open_with_comma(self):
        self.assertEqual(parse_move("3,5", 8, 8), ("open", 3, 5))

    def test_flag(self):
        self.assertEqual(parse_move("f 0 7", 8, 8), ("flag", 0, 7))

    def test_quit(self):
        self.assertEqual(parse_move("q", 8, 8), ("quit", 0, 0))

    def test_out_of_bounds(self):
        self.assertIsNone(parse_move("8 0", 8, 8))
        self.assertIsNone(parse_move("-1 0", 8, 8))

    def test_garbage(self):
        self.assertIsNone(parse_move("hello", 8, 8))
        self.assertIsNone(parse_move("", 8, 8))
        self.assertIsNone(parse_move("1 2 3", 8, 8))


if __name__ == "__main__":
    unittest.main()
