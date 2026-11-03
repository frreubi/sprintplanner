import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import unittest
from datetime import date
from medewerker import Medewerker
from rooster import Rooster
import rooster
from toewijzingen import Roostertoewijzing
from berekeningen import (
    bereken_roosteruren,
    bereken_afwezigheidsuren,
    bereken_netto_uren,
    bereken_netto_uren_per_periode,
    bereken_netto_uren_medewerkers,
    bereken_agile_overhead_per_dag,
)


class TestBerekenRoosteruren(unittest.TestCase):
    def setUp(self):
        r001 = Rooster("R001", 1, [[8, 8, 8, 8, 4]])
        r002 = Rooster("R002", 1, [[8, 8, 8, 8, 0]])
        vanaf = date(2026, 10, 19)

        self.medewerkers = [
            Medewerker("j001", "Jan", "van der", "Berg", "dev",{"dev": 100, "ops": 0, "func": 0}),
            Medewerker("p002", "Petra", "", "Jansen", "ops",{"dev": 0, "ops": 100, "func": 0}),
            Medewerker("a003", "Ahmed", "", "Bakker", "func",{"dev": 0, "ops": 0, "func": 100}),
        ]

        self.toewijzingen = [
            Roostertoewijzing(m, r, vanaf)
            for m, r in zip(self.medewerkers, [r001, r002, r001])
        ]

    def test_roosteruren_correct(self):
        resultaten = bereken_roosteruren(
            self.medewerkers,
            date(2026, 10, 19),
            date(2026, 10, 23),
            self.toewijzingen
        )
        verwacht = [
            ["j001", "Jan van der Berg",  36],
            ["p002", "Petra Jansen", 32],
            ["a003", "Ahmed Bakker", 36],
        ]
        self.assertEqual(resultaten, verwacht)
        
    def test_periode_over_twee_weken(self):
        resultaten = bereken_roosteruren(
            self.medewerkers,
            date(2026, 10, 19),
            date(2026, 10, 26),
            self.toewijzingen
        )
        self.assertEqual(resultaten[0][2], 44)

    def test_einddatum_voor_startdatum(self):
        with self.assertRaises(ValueError):
            bereken_roosteruren(
                self.medewerkers,
                date(2026, 10, 23),
                date(2026, 10, 19),
                self.toewijzingen
            )

    def test_ontbrekend_rooster(self):
        rooster = Rooster("R999", 1, [[8, 8, 8, 8, 4]])
        medewerker = Medewerker(
            "x004", "Sam", "", "Test", "dev", {"dev": 100, "ops": 0, "func": 0}
        )
        with self.assertRaisesRegex(ValueError, "Geen roostertoewijzing gevonden"):
            bereken_roosteruren(
                [medewerker],
                date(2026, 10, 19),
                date(2026, 10, 23),
                self.toewijzingen
            )
    

class TestBerekenAfwezigheidsuren(unittest.TestCase):
    def test_afwezigheid_met_uren(self):
        self.assertEqual(bereken_afwezigheidsuren("2V", 8), 2)
        self.assertEqual(bereken_afwezigheidsuren("6V", 8), 6)
        self.assertEqual(bereken_afwezigheidsuren("8V", 9), 8)

    def test_volledige_dag_afwezig(self):
        self.assertEqual(bereken_afwezigheidsuren("V", 8), 8)
        self.assertEqual(bereken_afwezigheidsuren("V", 4), 4)
        self.assertEqual(bereken_afwezigheidsuren("V", 0), 0)


class TestBerekenNettoUren(unittest.TestCase):
    def test_netto_uren(self):
        self.assertEqual(bereken_netto_uren(8, None), 8)
        self.assertEqual(bereken_netto_uren(8, "2V"), 6)
        self.assertEqual(bereken_netto_uren(8, "6V"), 2)
        self.assertEqual(bereken_netto_uren(9, "8V"), 1)
        self.assertEqual(bereken_netto_uren(4, "V"), 0)



class TestBerekenNettoUrenPerPeriode(unittest.TestCase):
    def test_netto_uren_met_afwezigheid(self):
        rooster = Rooster(
            "R001", 1, [[8, 8, 8, 8, 4]])
        
        afwezigheid = {
            date(2026, 10, 20): "2V",
            date(2026, 10, 22): "V",
        }

        totaal = bereken_netto_uren_per_periode(
            rooster,
            date(2026, 10, 19),
            date(2026, 10, 23),
            afwezigheid,
        )

        self.assertEqual(totaal, 26)


    def test_netto_uren_zonder_afwezigheid(self):
        rooster = Rooster(
            "R001", 1, [[8, 8, 8, 8, 4]])
        
        totaal = bereken_netto_uren_per_periode(
            rooster,
            date(2026, 10, 19),
            date(2026, 10, 23),
            {},
        )

        self.assertEqual(totaal, 36)

    def test_einddatum_voor_startdatum(self):
        rooster = Rooster(
            "R001", 1, [[8, 8, 8, 8, 4]])

        with self.assertRaises(ValueError):
            bereken_netto_uren_per_periode(
                rooster,
                date(2026, 10, 23),
                date(2026, 10, 19),
                {},
            )


class TestBerekenNettoUrenMedewerkers(unittest.TestCase):
    def test_netto_uren_per_medewerker(self):
        agile_instellingen = [
            {"type": "DagStart", "dagen": ["ma", "di", "do"], "duur": 0.5},
            {"type": "Refinement", "dagen": ["do"], "duur": 1.5},
            {"type": "Sprintwissel", "dagen": ["ma"], "duur": 3.0},
        ]    
        r001 = Rooster("R001", 1, [[8, 8, 8, 8, 4]])
        r002 = Rooster("R002", 1, [[8, 8, 8, 8, 0]])
        vanaf = date(2026, 4, 7)

        medewerkers = [
            Medewerker("jansj27", "Jan", "", "Janssen", "dev", {"dev": 60, "ops": 20, "func": 20}),
            Medewerker("petrp12", "Petra", "", "Peters", "ops", {"dev": 0, "ops": 100, "func": 0}),
            Medewerker("ahmed01", "Ahmed", "", "Ahmed", "func", {"dev": 0, "ops": 0, "func": 100}),
        ]

        toewijzingen = [
            Roostertoewijzing(medewerkers[0], r001, vanaf),
            Roostertoewijzing(medewerkers[1], r002, vanaf),
            Roostertoewijzing(medewerkers[2], r001, vanaf),
        ]

        afwezigheden = {
            "jansj27": {
                date(2026, 4, 13): "2V",
                date(2026, 4, 14): "V",
            },
            "petrp12": {date(2026, 4, 13): "6V"},
        }

        resultaten = bereken_netto_uren_medewerkers(
            medewerkers,
            date(2026, 4, 7),
            date(2026, 4, 25),
            afwezigheden,
            toewijzingen,
            agile_instellingen,
        )
        print(resultaten)

        self.assertEqual(resultaten[0][2], 79.5)
        self.assertEqual(resultaten[1][2], 71.0)
        self.assertEqual(resultaten[2][2], 89.0)
        self.assertEqual(sum(r[2] for r in resultaten), 239.5)


    def test_agile_overhead(self):
        rooster = Rooster("R001", 1, [[8, 8, 8, 8, 4]])
        medewerker = Medewerker("j001", "Jan", "", "Berg", "dev", {"dev": 100, "ops": 0, "func": 0})
        toewijzingen = [
            Roostertoewijzing(medewerker, rooster, date(2026, 10, 19))
        ]

        instellingen = [
            {"type": "DagStart", "dagen": ["ma", "di", "do"], "duur": 0.5},
            {"type": "Refinement", "dagen": ["do"], "duur": 1.5},
            {"type": "Sprintwissel", "dagen": ["ma"], "duur": 3.0},
        ]

        resultaat = bereken_agile_overhead_per_dag(
            medewerker,
            date(2026, 10, 19),
            date(2026, 10, 19),
            toewijzingen,
            instellingen,
            8,
        )

        self.assertEqual(resultaat, 3.0)

if __name__ == "__main__":
    unittest.main()
