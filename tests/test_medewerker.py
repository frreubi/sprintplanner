import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import date
from medewerker import Medewerker, controleer_rolpercentages

class TestMedewerker(unittest.TestCase):

    def test_geldige_medewerker(self):
        m = Medewerker("j001", "Jan", "van der", "Berg", "dev", {"dev": 60, "ops": 20, "func": 20})
        self.assertEqual(m.naam, "Jan van der Berg")
        self.assertIsNone(m.einddatum)

    def test_rolpercentages_en_controle(self):
        m = Medewerker("j001", "Jan", "", "Berg", "dev", {"dev": 60, "ops": 20, "func": 20})
        self.assertEqual(m.werkstromen, {"dev": 60, "ops": 20, "func": 20})
        self.assertEqual(controleer_rolpercentages([m]), [])

    def test_waarschuwing_rolpercentages_niet_100(self):
        m = Medewerker("j001", "Jan", "", "Berg", "dev", {"dev": 60, "ops": 20, "func": 10})
        waarschuwingen = controleer_rolpercentages([m])
        self.assertEqual(len(waarschuwingen), 1)
        self.assertIn("Jan Berg", waarschuwingen[0])
        self.assertIn("90%", waarschuwingen[0])

    def test_ongeldig_rolpercentage(self):
        with self.assertRaises(ValueError):
            Medewerker("j001", "Jan", "", "Berg", "dev", {"dev": 101, "ops": 0, "func": 0})

    def test_leeg_userid(self):
        with self.assertRaises(ValueError):
            Medewerker("", "Jan", "van der", "Berg", "dev", {"dev": 60, "ops": 20, "func": 20})

    def test_ongeldige_wijziging_voornaam(self):
        m = Medewerker("j001", "Jan", "van der", "Berg", "dev", {"dev": 60, "ops": 20, "func": 20})
        with self.assertRaises(ValueError):
            m.voornaam = ""

    def test_ongeldig_tussenvoegsel(self):
        m = Medewerker("j001", "Jan", "van der", "Berg", "dev", {"dev": 60, "ops": 20, "func": 20})
        with self.assertRaises(ValueError):
            m.tussenvoegsel = None

    def test_ongeldige_wijziging_achternaam(self):
        m = Medewerker("j001", "Jan", "van der", "Berg", "dev", {"dev": 60, "ops": 20, "func": 20})
        with self.assertRaises(ValueError):
            m.achternaam = ""

    def test_onbekende_rol(self):
        m = Medewerker(
            "j001", "Jan", "", "Berg", "architect",
            {"dev": 60, "ops": 20, "func": 20}
        )
        self.assertEqual(m.rol, "architect")

    def test_rol_wordt_kleine_letters(self):
        m = Medewerker("j001", "Jan", "van der", "Berg", "DEV", {"dev": 60, "ops": 20, "func": 20})
        self.assertEqual(m.rol, "dev")

    def test_einddatum_medewerker(self):
        m = Medewerker("p002", "Petra", "", "Jansen", "ops", {"dev": 60, "ops": 20, "func": 20}, einddatum=date(2030, 10, 15))
        self.assertEqual(m.einddatum, date(2030, 10, 15))

    def test_einddatum_onbekend(self):
        m = Medewerker("p002", "Petra", "", "Jansen", "ops", {"dev": 60, "ops": 20, "func": 20})
        self.assertIsNone(m.einddatum)

    def test_ongeldige_einddatum(self):
        with self.assertRaises(ValueError):
            Medewerker("p002", "Petra", "", "Jansen", "ops", {"dev": 60, "ops": 20, "func": 20}, einddatum="15-10-2030")

    def test_ongeldige_beheerder(self):
        with self.assertRaises(ValueError):
            Medewerker("j001", "Jan", "", "Berg", "dev", {"dev": 60, "ops": 20, "func": 20}, beheerder="ja")

    def test_ongeldige_access_analist(self):
        with self.assertRaises(ValueError):
            Medewerker("j001", "Jan", "", "Berg", "dev", {"dev": 60, "ops": 20, "func": 20}, access_analist=1)

