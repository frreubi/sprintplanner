import unittest
from datetime import date
from berekeningen import bereken_sprintresultaten
from medewerker import Medewerker
from rooster import Rooster
from toewijzingen import Roostertoewijzing

class TestSprintresultaten(unittest.TestCase):
    def setUp(self):
        self.medewerker = Medewerker(
            "j001", "Jan", "van der", "Berg",
            "dev",
            {"dev": 60, "ops": 20, "func": 20},
        )
        
        self.rooster = Rooster(
            "R1",
            1,
            [[8, 8, 8, 8, 8]],
        )

        self.toewijzing = Roostertoewijzing(
            self.medewerker,
            self.rooster,
            date(2026, 1, 5),
            date(2026, 1, 9),
        )
        self.afwezigheden = {}
        self.agile_instellingen = []
        self.uren_per_storypoint = 4

    def test_storypoints_per_medewerker(self):
        resultaten = bereken_sprintresultaten(
            [self.medewerker],
            date(2026, 1, 5),
            date(2026, 1, 9),
            self.afwezigheden,
            [self.toewijzing],
            self.agile_instellingen,
            self.uren_per_storypoint,
        )

        self.assertEqual(len(resultaten), 1)
        self.assertEqual(resultaten[0]["uren"], 40)
        self.assertEqual(resultaten[0]["storypoints"], 10)
        self.assertEqual(
            resultaten[0]["storypoints_per_werkstroom"],
            {"dev": 6, "ops": 2, "func": 2},
        )