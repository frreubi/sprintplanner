import json
import unittest

from applicatie import verwerk_contract
from tests.test_contract import voorbeeld


class TestApplicatieContract(unittest.TestCase):

    def test_applicatie_verwerkt_json_en_levert_sprintinfo_data(self):
        resultaat = verwerk_contract(json.dumps(voorbeeld()))

        self.assertEqual(len(resultaat), 1)
        self.assertEqual(resultaat[0]["naam"], "Sprint 2026-Week 45")
        self.assertEqual(resultaat[0]["begindatum"], "2026-11-02")
        self.assertEqual(len(resultaat[0]["netto_uren"]), 1)
        self.assertEqual(resultaat[0]["netto_uren"][0]["userid"], "j001")

    def test_medewerker_na_einddatum_wordt_niet_meegenomen(self):
        data = voorbeeld()
        data["medewerkers"][0]["einddatum"] = "2026-11-02"

        resultaat = verwerk_contract(json.dumps(data))

        medewerker = resultaat[0]["netto_uren"][0]
        self.assertEqual(medewerker["uren"], 8)

    def test_ongeldige_payload_stopt_verwerking(self):
        data = voorbeeld()
        data["toewijzingen"] = []

        with self.assertRaises(ValueError):
            verwerk_contract(json.dumps(data))


if __name__ == "__main__":
    unittest.main()
