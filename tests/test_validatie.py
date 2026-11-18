import json
import unittest
from datetime import date

from contract import laad_contract
from tests.test_contract import voorbeeld
from validatie import valideer_sprintgegevens
from percentages import Percentageverdeling
from toewijzingen import PercentageToewijzing


class TestValideerSprintgegevens(unittest.TestCase):

    def valideer(self, data):
        gegevens = laad_contract(json.dumps(data))
        sprint = gegevens["sprints"][0]
        return valideer_sprintgegevens(
            gegevens["medewerkers"],
            sprint.begindatum,
            sprint.einddatum,
            gegevens["afwezigheid_records"],
            gegevens["toewijzingen"],
        )

    def test_foutieve_code_buiten_sprint_blokkeert_niet(self):
        data = voorbeeld()
        data["afwezigheden"].append({
            "userid": "j001",
            "datum": "2026-01-05",
            "code": "X",
        })

        self.assertEqual(self.valideer(data), [])

    def test_foutieve_code_binnen_sprint_wordt_gemeld(self):
        data = voorbeeld()
        data["afwezigheden"][0]["code"] = "X"

        fouten = self.valideer(data)

        self.assertEqual(len(fouten), 1)
        self.assertIn("Ongeldige afwezigheidscode", fouten[0])
        self.assertIn("2026-11-03", fouten[0])

    def test_afwezigheid_op_feestdag_wordt_genegeerd(self):
        data = voorbeeld()
        data["instellingen"]["datum_eerste_sprint"] = "2026-12-25"
        data["afwezigheden"] = [{
            "userid": "j001",
            "datum": "2026-12-25",
            "code": "X",
        }]

        self.assertEqual(self.valideer(data), [])

    def test_dagen_buiten_dienstverband_worden_genegeerd(self):
        data = voorbeeld()
        data["medewerkers"][0]["startdatum"] = "2026-11-04"
        data["medewerkers"][0]["einddatum"] = "2026-11-04"
        data["toewijzingen"][0]["geldig_vanaf"] = "2026-11-04"
        data["afwezigheden"] = [
            {"userid": "j001", "datum": "2026-11-02", "code": "X"},
            {"userid": "j001", "datum": "2026-11-06", "code": "X"},
        ]

        self.assertEqual(self.valideer(data), [])

    def test_ontbrekende_roostertoewijzing_wordt_gemeld(self):
        data = voorbeeld()
        data["toewijzingen"][0]["geldig_vanaf"] = "2026-11-03"

        fouten = self.valideer(data)

        self.assertEqual(len(fouten), 1)
        self.assertIn("2026-11-02", fouten[0])
        self.assertIn("geen rooster toegewezen", fouten[0])

    def test_meerdere_percentage_toewijzingen_worden_gemeld(self):
        data = voorbeeld()
        gegevens = laad_contract(json.dumps(data))
        medewerker = gegevens["medewerkers"][0]
        verdeling = Percentageverdeling("P02", {"ops": 0.1})
        extra = PercentageToewijzing(
            medewerker, verdeling,
            date(2026, 11, 3), date(2026, 11, 3)
        )
        fouten = valideer_sprintgegevens(
            gegevens["medewerkers"],
            gegevens["sprints"][0].begindatum,
            gegevens["sprints"][0].einddatum,
            gegevens["afwezigheid_records"],
            gegevens["toewijzingen"] + [extra],
        )
        self.assertEqual(len(fouten), 1)
        self.assertIn("meerdere percentage-toewijzingen", fouten[0])

    def test_meerdere_fouten_worden_verzameld(self):
        data = voorbeeld()
        data["toewijzingen"][0]["geldig_vanaf"] = "2026-11-03"
        data["afwezigheden"] = [
            {"userid": "j001", "datum": "2026-11-03", "code": "X"},
            {"userid": "j001", "datum": "2026-11-04", "code": "4V"},
            {"userid": "j001", "datum": "2026-11-04", "code": "V"},
        ]

        fouten = self.valideer(data)

        self.assertEqual(len(fouten), 3)
        self.assertTrue(any("2026-11-02" in fout for fout in fouten))
        self.assertTrue(any("Ongeldige afwezigheidscode" in fout for fout in fouten))
        self.assertTrue(any("meer dan één afwezigheidsregistratie" in fout for fout in fouten))


if __name__ == "__main__":
    unittest.main()
