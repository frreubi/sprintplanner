import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import unittest
from datetime import date, timedelta
from kalender import (
    eerste_roostermaandag,
    einde_rooster,
    datums_roosterjaar,
    maandkoppen_roosterjaar,
)

class TestEersteRoostermaandag(unittest.TestCase):
    def test_jaar_2026(self):
        self.assertEqual(eerste_roostermaandag(2026), date(2025, 12, 29))

    def test_jaar_2027(self):
        self.assertEqual(eerste_roostermaandag(2027), date(2027, 1, 4))

    def test_resultaat_is_altijd_maandag(self):
        for jaar in range(2020, 2041):
            with self.subTest(jaar=jaar):
                datum = eerste_roostermaandag(jaar)
                self.assertEqual(datum.weekday(), 0)

    def test_einde_rooster_2026(self):
        self.assertEqual(einde_rooster(2026), date(2027, 1, 4))

    def test_rooster_heeft_altijd_371_dagen(self):
        for jaar in range(2020, 2041):
            with self.subTest(jaar=jaar):
                begin = eerste_roostermaandag(jaar)
                einde = einde_rooster(jaar)
                self.assertEqual((einde - begin).days, 371)
                self.assertEqual(einde.weekday(), 0)

    def test_datums_roosterjaar(self):
        datums = datums_roosterjaar(2026)

        self.assertEqual(len(datums), 371)
        self.assertEqual(datums[0], date(2025, 12, 29))
        self.assertEqual(datums[-1], date(2027, 1, 3))
        self.assertEqual(datums[0].weekday(), 0)
        self.assertEqual(datums[-1] + timedelta(days=1), einde_rooster(2026))  
                  
    def test_maandkoppen_bevatten_twaalf_maanden(self):
        koppen = maandkoppen_roosterjaar(2026)

        self.assertEqual(len(koppen), 12)
        self.assertEqual(
            [kop[0] for kop in koppen],
            [
                "JANUARI", "FEBRUARI", "MAART", "APRIL",
                "MEI", "JUNI", "JULI", "AUGUSTUS",
                "SEPTEMBER", "OKTOBER", "NOVEMBER", "DECEMBER",
            ],
        )

        datums = datums_roosterjaar(2026)
        for maandnummer, (_, begin, einde) in enumerate(koppen, start=1):
            self.assertEqual(datums[begin].month, maandnummer)
            self.assertEqual(datums[begin].year, 2026)
            self.assertEqual(datums[einde].month, maandnummer)
            self.assertEqual(datums[einde].year, 2026)


if __name__ == "__main__":
    unittest.main()