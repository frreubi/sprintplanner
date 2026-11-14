import unittest
from datetime import date

from berekeningen import bereken_sprintresultaten
from medewerker import Medewerker
from percentages import Percentageverdeling
from rollen import Rol
from rooster import Rooster
from toewijzingen import Roostertoewijzing, PercentageToewijzing


class TestSprintresultaten(unittest.TestCase):
    def setUp(self):
        self.medewerker = Medewerker(
            "j001", "Jan", "van der", "Berg", "dev"
        )
        self.rol = Rol(
            "dev", "Developer", "dev",
            date(2025, 1, 1)
        )
        self.rollen = {"dev": self.rol}
        self.rooster = Rooster("R1", 1, [[8, 8, 8, 8, 8]])
        self.roostertoewijzing = Roostertoewijzing(
            self.medewerker, self.rooster,
            date(2026, 1, 5), date(2026, 1, 9)
        )
        self.afwezigheden = {}
        self.agile_instellingen = []
        self.uren_per_storypoint = 4

    def bereken(self, extra_toewijzingen=None):
        toewijzingen = [self.roostertoewijzing]
        if extra_toewijzingen:
            toewijzingen.extend(extra_toewijzingen)
        return bereken_sprintresultaten(
            [self.medewerker],
            date(2026, 1, 5),
            date(2026, 1, 9),
            self.afwezigheden,
            toewijzingen,
            self.agile_instellingen,
            self.uren_per_storypoint,
            self.rollen,
        )

    def test_storypoints_per_medewerker(self):
        percentage = Percentageverdeling(
            "P01", {"dev": 0.6, "ops": 0.2, "func": 0.2}
        )
        toewijzing = PercentageToewijzing(
            self.medewerker, percentage,
            date(2026, 1, 5), date(2026, 1, 9)
        )

        resultaat = self.bereken([toewijzing])

        self.assertEqual(len(resultaat), 1)
        self.assertEqual(resultaat[0]["uren"], 40)
        self.assertEqual(resultaat[0]["storypoints"], 10)
        self.assertEqual(
            resultaat[0]["storypoints_per_werkstroom"],
            {"dev": 6, "ops": 2, "func": 2},
        )

    def test_standaardwerkstroom_vult_aan_zonder_percentage(self):
        resultaat = self.bereken()
        self.assertEqual(resultaat[0]["uren_per_werkstroom"], {"dev": 40.0})
        self.assertEqual(resultaat[0]["storypoints"], 10)

    def test_andere_werkstroom_wordt_afgetrokken_van_standaard(self):
        percentage = Percentageverdeling("P02", {"ops": 0.25})
        toewijzing = PercentageToewijzing(
            self.medewerker, percentage,
            date(2026, 1, 5), date(2026, 1, 9)
        )
        resultaat = self.bereken([toewijzing])
        self.assertEqual(
            resultaat[0]["uren_per_werkstroom"],
            {"ops": 10.0, "dev": 30.0},
        )

    def test_volledige_toewijzing_aan_andere_werkstroom(self):
        percentage = Percentageverdeling("P04", {"ops": 1.0})
        toewijzing = PercentageToewijzing(
            self.medewerker, percentage,
            date(2026, 1, 5), date(2026, 1, 9)
        )
        resultaat = self.bereken([toewijzing])
        self.assertEqual(resultaat[0]["uren_per_werkstroom"], {
            "ops": 40.0, "dev": 0.0
        })
        self.assertEqual(resultaat[0]["storypoints_per_werkstroom"], {
            "ops": 10, "dev": 0
        })

    def test_explicit_eigen_werkstroom_laat_rest_buiten_sprintwerk(self):
        percentage = Percentageverdeling("P03", {"dev": 0.8})
        toewijzing = PercentageToewijzing(
            self.medewerker, percentage,
            date(2026, 1, 5), date(2026, 1, 9)
        )
        resultaat = self.bereken([toewijzing])
        self.assertEqual(resultaat[0]["uren_per_werkstroom"], {"dev": 32.0})
        self.assertEqual(resultaat[0]["storypoints"], 8)


if __name__ == "__main__":
    unittest.main()
