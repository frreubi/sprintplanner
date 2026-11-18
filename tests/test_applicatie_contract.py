import json
import unittest

from applicatie import verwerk_contract
from tests.test_contract import voorbeeld


class TestApplicatieContract(unittest.TestCase):

    def test_applicatie_verwerkt_json_en_levert_sprintinfo_data(self):
        resultaat = verwerk_contract(json.dumps(voorbeeld()))

        self.assertGreater(len(resultaat), 1)
        self.assertEqual(resultaat[0]["sprintID"], 1)
        self.assertNotIn("naam", resultaat[0])
        self.assertEqual(resultaat[0]["begindatum"], "2026-11-02")
        self.assertEqual(resultaat[0]["einddatum"], "2026-11-08")
        self.assertEqual(len(resultaat[0]["netto_uren"]), 1)
        self.assertEqual(resultaat[0]["netto_uren"][0]["userid"], "j001")

    def test_medewerker_na_einddatum_wordt_niet_meegenomen(self):
        data = voorbeeld()
        data["medewerkers"][0]["einddatum"] = "2026-11-02"

        resultaat = verwerk_contract(json.dumps(data))

        medewerker = resultaat[0]["netto_uren"][0]
        self.assertEqual(medewerker["uren"], 8)

    def test_sprint_met_ontbrekende_roostertoewijzing_krijgt_fouten(self):
        data = voorbeeld()
        data["toewijzingen"] = []

        resultaat = verwerk_contract(json.dumps(data))

        self.assertEqual(resultaat[0]["netto_uren"], [])
        self.assertTrue(resultaat[0]["fouten"])
        self.assertIn("geen rooster toegewezen", resultaat[0]["fouten"][0])

    def test_fout_in_een_sprint_blokkeert_andere_sprint_niet(self):
        data = voorbeeld()
        data["afwezigheden"][0]["code"] = "X"

        resultaat = verwerk_contract(json.dumps(data))

        self.assertGreater(len(resultaat), 1)

        self.assertTrue(resultaat[0]["fouten"])
        self.assertEqual(resultaat[0]["netto_uren"], [])

        self.assertEqual(resultaat[1]["fouten"], [])
        self.assertEqual(len(resultaat[1]["netto_uren"]), 1)
        self.assertEqual(resultaat[1]["netto_uren"][0]["userid"], "j001")


if __name__ == "__main__":
    unittest.main()
