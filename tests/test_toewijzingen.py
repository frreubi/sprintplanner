import unittest
from datetime import date
from medewerker import Medewerker
from rooster import Rooster
from toewijzingen import Roostertoewijzing, zoek_toewijzing


class TestRoostertoewijzing(unittest.TestCase):

    def setUp(self):
        self.rooster = Rooster("R001", 1, [[8, 8, 8, 8, 4]])
        self.medewerker = Medewerker(
            "p002", "Petra", "", "Jansen", "ops",
            {"dev": 0, "ops": 100, "func": 0}
        )

    def test_geldigheid_datums(self):
        toewijzing = Roostertoewijzing(
            self.medewerker, self.rooster,
            date(2026, 1, 5), date(2026, 1, 9)
        )

        self.assertTrue(toewijzing.geldt_op(date(2026, 1, 5)))
        self.assertTrue(toewijzing.geldt_op(date(2026, 1, 9)))
        self.assertFalse(toewijzing.geldt_op(date(2026, 1, 4)))
        self.assertFalse(toewijzing.geldt_op(date(2026, 1, 10)))

    def test_doorlopende_toewijzing(self):
        toewijzing = Roostertoewijzing(
            self.medewerker, self.rooster, date(2026, 1, 5)
        )
        self.assertTrue(toewijzing.geldt_op(date(2026, 12, 31)))

    def test_ongeldige_geldigheidsperiode(self):
        with self.assertRaises(ValueError):
            Roostertoewijzing(
                self.medewerker, self.rooster,
                date(2026, 1, 9), date(2026, 1, 5)
            )


class TestEinddatumMedewerker(unittest.TestCase):

    def test_einddatum_medewerker(self):
        medewerker = Medewerker(
            "p002", "Petra", "", "Jansen", "ops",
            {"dev": 0, "ops": 100, "func": 0},
            einddatum=date(2030, 10, 15)
        )
        self.assertEqual(medewerker.einddatum, date(2030, 10, 15))

    def test_einddatum_onbekend(self):
        medewerker = Medewerker(
            "p002", "Petra", "", "Jansen", "ops",
            {"dev": 0, "ops": 100, "func": 0}
        )
        self.assertIsNone(medewerker.einddatum)

    def test_ongeldige_einddatum(self):
        with self.assertRaises(ValueError):
            Medewerker(
                "p002", "Petra", "", "Jansen", "ops",
                {"dev": 0, "ops": 100, "func": 0},
                einddatum="15-10-2030"
            )


class TestZoekToewijzing(unittest.TestCase):

    def setUp(self):
        medewerker = Medewerker(
            "p002", "Petra", "", "Jansen", "ops",
            {"dev": 0, "ops": 100, "func": 0}
        )
        rooster = Rooster("R001", 1, [[8, 8, 8, 8, 4]])
        rooster_nieuw = Rooster("R002", 1, [[9, 9, 9, 4, 0]])

        self.eerste = Roostertoewijzing(
            medewerker, rooster, date(2026, 1, 5), date(2026, 1, 9)
        )
        self.tweede = Roostertoewijzing(
            medewerker, rooster_nieuw, date(2026, 1, 12)
        )
        self.medewerker = medewerker
        self.toewijzingen = [self.eerste, self.tweede]

    def test_juiste_toewijzing_gevonden(self):
        self.assertIs(
            zoek_toewijzing(
                self.medewerker, date(2026, 1, 7), self.toewijzingen
            ),
            self.eerste,
        )
        self.assertIs(
            zoek_toewijzing(
                self.medewerker, date(2026, 1, 12), self.toewijzingen
            ),
            self.tweede,
        )

    def test_geen_toewijzing_gevonden(self):
        with self.assertRaisesRegex(ValueError, "Geen roostertoewijzing"):
            zoek_toewijzing(
                self.medewerker, date(2026, 1, 4), self.toewijzingen
            )

    def test_meerdere_toewijzingen(self):
        overlap = Roostertoewijzing(
            self.medewerker, self.tweede.rooster, date(2026, 1, 8)
        )

        with self.assertRaisesRegex(ValueError, "Meerdere roostertoewijzingen"):
            zoek_toewijzing(
                self.medewerker, date(2026, 1, 8),
                [self.eerste, overlap]
            )


if __name__ == "__main__":
    unittest.main()