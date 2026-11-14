
import unittest
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from medewerker import Medewerker


class TestMedewerker(unittest.TestCase):

    def maak_medewerker(self, **kwargs):
        gegevens = {
            "userid": "j001",
            "voornaam": "Jan",
            "tussenvoegsel": "van der",
            "achternaam": "Berg",
            "rol": "dev",
        }
        gegevens.update(kwargs)
        return Medewerker(**gegevens)

    def test_geldige_medewerker(self):
        m = self.maak_medewerker()

        self.assertEqual(m.naam, "Jan van der Berg")
        self.assertEqual(m.rol, "dev")
        self.assertIsNone(m.einddatum)

    def test_leeg_userid(self):
        with self.assertRaises(ValueError):
            self.maak_medewerker(userid="")

    def test_ongeldige_wijziging_voornaam(self):
        m = self.maak_medewerker()
        with self.assertRaises(ValueError):
            m.voornaam = ""

    def test_ongeldig_tussenvoegsel(self):
        m = self.maak_medewerker()
        with self.assertRaises(ValueError):
            m.tussenvoegsel = None

    def test_ongeldige_wijziging_achternaam(self):
        m = self.maak_medewerker()
        with self.assertRaises(ValueError):
            m.achternaam = ""

    def test_onbekende_rol(self):
        m = self.maak_medewerker(rol="architect")
        self.assertEqual(m.rol, "architect")

    def test_rol_wordt_kleine_letters(self):
        m = self.maak_medewerker(rol="DEV")
        self.assertEqual(m.rol, "dev")

    def test_einddatum_medewerker(self):
        einddatum = date(2030, 10, 15)
        m = self.maak_medewerker(einddatum=einddatum)
        self.assertEqual(m.einddatum, einddatum)

    def test_einddatum_onbekend(self):
        m = self.maak_medewerker()
        self.assertIsNone(m.einddatum)

    def test_ongeldige_einddatum(self):
        with self.assertRaises(ValueError):
            self.maak_medewerker(einddatum="15-10-2030")

    def test_ongeldige_beheerder(self):
        with self.assertRaises(ValueError):
            self.maak_medewerker(beheerder="ja")

    def test_ongeldige_access_analist(self):
        with self.assertRaises(ValueError):
            self.maak_medewerker(access_analist=1)
