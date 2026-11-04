import unittest
from datetime import date
from rooster import Rooster


class TestRooster(unittest.TestCase):

    def test_tweewekelijks_rooster(self):
        rooster = Rooster(
            "R001",
            2,
            [
                [7, 7, 7, 8, 8],
                [8, 8, 8, 8, 7],
            ],
        )

        self.assertEqual(rooster.uren_op(date(2026, 10, 19)), 7)
        self.assertEqual(rooster.uren_op(date(2026, 10, 26)), 8)
        self.assertEqual(rooster.uren_op(date(2026, 10, 24)), 0)

    def test_eenwekelijks_rooster(self):
        rooster = Rooster(
            "R003",
            1,
            [[8, 8, 8, 8, 0]],
        )

        self.assertEqual(rooster.uren_op(date(2026, 10, 19)), 8)
        self.assertEqual(rooster.uren_op(date(2026, 10, 26)), 8)

    def test_ongeldige_cyclus(self):
        with self.assertRaises(ValueError):
            Rooster("R004", 3, [[8, 8, 8, 8, 8]])


if __name__ == "__main__":
    unittest.main()