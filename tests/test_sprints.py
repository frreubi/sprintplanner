import unittest
from datetime import date
from sprints import zoek_sprint


class TestZoekSprint(unittest.TestCase):

    def setUp(self):
        self.sprints = [
            {
                "naam": "2026-44",
                "begindatum": date(2026, 10, 26),
                "einddatum": date(2026, 11, 13),
            }
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
            {
                "naam": "2026-45",
                "begindatum": date(2026, 11, 10),
                "einddatum": date(2026, 11, 20),
            }
        ]

        with self.assertRaises(ValueError):
            zoek_sprint(date(2026, 11, 12), overlap)


if __name__ == "__main__":
    unittest.main()