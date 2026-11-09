import json
import unittest
from datetime import date

from contract import laad_contract, ContractValidatieFout
from medewerker import Medewerker
from rooster import Rooster
from toewijzingen import Roostertoewijzing
from sprints import Sprint, zoek_sprint


def voorbeeld():
    return {
        "contract": {"naam": "Sprintplanner", "versie": "2.0"},
        "sprints": [{
            "naam": "Sprint 2026-Week 45",
            "begindatum": "2026-11-02",
            "einddatum": "2026-11-06",
        }],
        "medewerkers": [{
            "userid": "j001",
            "voornaam": "Jan",
            "tussenvoegsel": "",
            "achternaam": "Berg",
            "rol": "dev",
            "werkstromen": {"dev": 70, "ops": 20, "func": 10},
            "beheerder": False,
            "access_analist": False,
            "einddatum": None,
        }],
        "roosters": [{
            "rooster_id": "R01",
            "cyclus_weken": 1,
            "uren_per_week": [[8, 8, 8, 8, 4]],
        }],
        "toewijzingen": [{
            "userid": "j001",
            "rooster_id": "R01",
            "geldig_vanaf": "2026-01-01",
            "geldig_tm": None,
        }],
        "afwezigheden": [{
            "userid": "j001",
            "datum": "2026-11-03",
            "code": "4V",
        }],
        "agile_instellingen": [{
            "type": "DagStart",
            "dagen": ["ma", "di", "do"],
            "duur": 0.5,
        }],
        "instellingen": {
            "uren_per_storypoint": 6.0,
            "werkstromen": ["dev", "ops", "func"],
        },
    }


class TestContract(unittest.TestCase):

    def test_json_wordt_domeinobjecten(self):
        gegevens = laad_contract(json.dumps(voorbeeld()))

        self.assertIsInstance(gegevens["sprints"][0], Sprint)
        self.assertIsInstance(gegevens["medewerkers"][0], Medewerker)
        self.assertIsInstance(gegevens["roosters"]["R01"], Rooster)
        self.assertIsInstance(gegevens["toewijzingen"][0], Roostertoewijzing)
        self.assertEqual(
            gegevens["afwezigheden"]["j001"][date(2026, 11, 3)],
            "4V",
        )
        self.assertEqual(gegevens["uren_per_storypoint"], 6.0)

    def test_sprintobject_werkt_met_zoek_sprint(self):
        gegevens = laad_contract(json.dumps(voorbeeld()))
        sprint = gegevens["sprints"][0]

        self.assertIs(
            zoek_sprint(date(2026, 11, 4), gegevens["sprints"]),
            sprint,
        )

    def test_uitbreidingsvelden_worden_genegeerd(self):
        data = voorbeeld()
        data["extra_veld"] = {"later": True}
        data["medewerkers"][0]["toekomstig_veld"] = "waarde"

        gegevens = laad_contract(json.dumps(data))

        self.assertEqual(len(gegevens["medewerkers"]), 1)

    def test_onbekende_contractversie(self):
        data = voorbeeld()
        data["contract"]["versie"] = "3.0"

        with self.assertRaises(ContractValidatieFout) as context:
            laad_contract(json.dumps(data))

        self.assertEqual(
            context.exception.foutcode,
            "CONTRACTVERSIE_NIET_ONDERSTEUND",
        )

    def test_ontbrekende_roostertoewijzing_is_harde_fout(self):
        data = voorbeeld()
        data["toewijzingen"] = []

        with self.assertRaises(ContractValidatieFout) as context:
            laad_contract(json.dumps(data))

        self.assertEqual(
            context.exception.foutcode,
            "ROOSTERTOEWIJZING_ONTBREEKT",
        )
        self.assertIn("2026-11-02", context.exception.omschrijving)

    def test_roosterovergang_over_weekend_is_geldig(self):
        data = voorbeeld()
        data["sprints"][0]["begindatum"] = "2026-10-19"
        data["sprints"][0]["einddatum"] = "2026-10-30"

        data["roosters"].append({
            "rooster_id": "R02",
            "cyclus_weken": 1,
            "uren_per_week": [[8, 8, 8, 8, 4]],
        })

        data["toewijzingen"][0]["geldig_tm"] = "2026-10-23"
        data["toewijzingen"].append({
            "userid": "j001",
            "rooster_id": "R02",
            "geldig_vanaf": "2026-10-26",
            "geldig_tm": None,
        })

        gegevens = laad_contract(json.dumps(data))

        self.assertEqual(len(gegevens["toewijzingen"]), 2)

    def test_roostertoewijzing_op_maandag_na_weekend_verplicht(self):
        data = voorbeeld()
        data["sprints"][0]["begindatum"] = "2026-10-19"
        data["sprints"][0]["einddatum"] = "2026-10-30"

        data["roosters"].append({
            "rooster_id": "R02",
            "cyclus_weken": 1,
            "uren_per_week": [[8, 8, 8, 8, 4]],
        })

        data["toewijzingen"][0]["geldig_tm"] = "2026-10-23"
        data["toewijzingen"].append({
            "userid": "j001",
            "rooster_id": "R02",
            "geldig_vanaf": "2026-10-27",
            "geldig_tm": None,
        })

        with self.assertRaises(ContractValidatieFout) as context:
            laad_contract(json.dumps(data))

        self.assertEqual(
            context.exception.foutcode,
            "ROOSTERTOEWIJZING_ONTBREEKT",
        )
        self.assertIn("2026-10-26", context.exception.omschrijving)

    def test_roosteruren_boven_negen_afgekeurd(self):
        data = voorbeeld()
        data["roosters"][0]["uren_per_week"][0][0] = 10

        with self.assertRaises(ContractValidatieFout) as context:
            laad_contract(json.dumps(data))

        self.assertEqual(context.exception.foutcode, "ONGELDIG_GETAL")

    def test_roosteruren_met_decimalen_afgekeurd(self):
        data = voorbeeld()
        data["roosters"][0]["uren_per_week"][0][0] = 7.5

        with self.assertRaises(ContractValidatieFout):
            laad_contract(json.dumps(data))

    def test_onbekende_afwezigheidscode_afgekeurd(self):
        data = voorbeeld()
        data["afwezigheden"][0]["code"] = "X"

        with self.assertRaises(ContractValidatieFout) as context:
            laad_contract(json.dumps(data))

        self.assertEqual(
            context.exception.foutcode,
            "ONGELDIGE_AFWEZIGHEIDSCODE",
        )

    def test_afwezigheid_na_einddatum_genegeerd(self):
        data = voorbeeld()
        data["medewerkers"][0]["einddatum"] = "2026-11-02"
        data["afwezigheden"][0]["datum"] = "2026-11-03"

        gegevens = laad_contract(json.dumps(data))

        self.assertEqual(gegevens["afwezigheden"]["j001"], {})

    def test_fout_is_machineleesbaar(self):
        data = voorbeeld()
        data["instellingen"]["uren_per_storypoint"] = 0

        with self.assertRaises(ContractValidatieFout) as context:
            laad_contract(json.dumps(data))

        fout = context.exception.als_dict()
        self.assertEqual(
            set(fout),
            {"foutcode", "onderdeel", "gegevenspad", "omschrijving"},
        )


if __name__ == "__main__":
    unittest.main()
