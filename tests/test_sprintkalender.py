import unittest
from datetime import date, timedelta

from sprintkalender import genereer_sprints


class TestSprintkalender(unittest.TestCase):

    def test_sprints_drie_weken_heel_jaar(self):
        sprints = genereer_sprints(date(2026, 1, 5), 3)

        self.assertEqual(len(sprints), 18)
        self.assertEqual(sprints[0].sprintID, 1)
        self.assertEqual(sprints[0].begindatum, date(2026, 1, 5))
        self.assertEqual(sprints[0].einddatum, date(2026, 1, 25))

        self.assertEqual(sprints[-1].begindatum, date(2026, 12, 28))
        self.assertEqual(sprints[-1].einddatum, date(2027, 1, 17))

    def test_sprints_sluiten_op_elkaar_aan(self):
        sprints = genereer_sprints(date(2026, 1, 5), 3)

        for vorige, volgende in zip(sprints, sprints[1:]):
            self.assertEqual(
                volgende.begindatum,
                vorige.einddatum + timedelta(days=1),
            )

    def test_sprintduur_twee_weken(self):
        sprints = genereer_sprints(date(2026, 1, 5), 2)

        self.assertEqual(sprints[0].einddatum, date(2026, 1, 18))
        self.assertEqual(sprints[1].begindatum, date(2026, 1, 19))

    def test_sprintduur_nul_is_ongeldig(self):
        with self.assertRaises(ValueError):
            genereer_sprints(date(2026, 1, 5), 0)


if __name__ == "__main__":
    unittest.main()