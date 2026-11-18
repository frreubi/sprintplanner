import unittest
from datetime import date
from sprints import Sprint, zoek_sprint


class TestZoekSprint(unittest.TestCase):

    def setUp(self):
        self.sprints = [
            Sprint(1, date(2026, 10, 26), date(2026, 11, 13))
        ]

    def test_sprint_gevonden(self):
        self.assertEqual(
            zoek_sprint(date(2026, 11, 2), self.sprints),
            self.sprints[0],
        )

    def test_geen_sprint_gevonden(self):
        self.assertIsNone(
            zoek_sprint(date(2026, 11, 14), self.sprints)
        )

    def test_overlappende_sprints(self):
        overlap = self.sprints + [
            Sprint(2, date(2026, 11, 10), date(2026, 11, 20))
        ]

        with self.assertRaises(ValueError):
            zoek_sprint(date(2026, 11, 12), overlap)


if __name__ == "__main__":
    unittest.main()