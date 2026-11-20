import json
import unittest
from datetime import date

from contract import laad_contract, ContractValidatieFout
from Domein.medewerker import Medewerker
from Domein.rooster import Rooster
from Domein.rollen import Rol
from Domein.percentages import Percentageverdeling
from Domein.toewijzingen import Roostertoewijzing, PercentageToewijzing
from Domein.sprints import Sprint, zoek_sprint


def voorbeeld():
    return {
        "contract": {"naam": "Sprintplanner", "versie": "5.0"},
        "rollen": [{
            "rol_id": "dev",
            "naam": "Developer",
            "doet_sprintwerk": True,
            "geldig_vanaf": "2025-01-01",
            "geldig_tm": None,
        }],
        "medewerkers": [{
            "userid": "j001",
            "voornaam": "Jan",
            "tussenvoegsel": "",
            "achternaam": "Berg",
            "rol": "dev",
            "beheerder": False,
            "access_analist": False,
            "startdatum": "2025-01-01",
            "einddatum": None,
        }],
        "roosters": [{
            "rooster_id": "R01",
            "cyclus_weken": 1,
            "uren_per_week": [[8, 8, 8, 8, 4]],
        }],
        "percentages": [{
            "percentage_id": "P001",
            "verdeling": {"dev": 0.7, "ops": 0.2, "func": 0.1},
        }],
        "toewijzingen": [{
            "userid": "j001",
            "type": "Rooster",
            "toewijzing_id": "R01",
            "geldig_vanaf": "2026-01-01",
            "geldig_tm": None,
        }, {
            "userid": "j001",
            "type": "Percentage",
            "toewijzing_id": "P001",
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
            "ma": True,
            "di": True,
            "wo": False,
            "do": True,
            "vr": False,
            "duur": 0.5,
        }],
        "instellingen": {
            "datum_eerste_sprint": "2026-11-02",
            "standaard_sprintduur": 1,
            "storypoints_accessman_rapportage": 1,
            "uren_per_storypoint": 6.0,
        },
    }


class TestContract(unittest.TestCase):

    def test_json_wordt_domeinobjecten(self):
        gegevens = laad_contract(json.dumps(voorbeeld()))

        self.assertIsInstance(gegevens["sprints"][0], Sprint)
        self.assertEqual(gegevens["sprints"][0].sprintID, 1)
        self.assertEqual(gegevens["sprints"][0].begindatum, date(2026, 11, 2))
        self.assertEqual(gegevens["sprints"][0].einddatum, date(2026, 11, 8))
        self.assertIsInstance(gegevens["rollen"]["dev"], Rol)
        self.assertEqual(gegevens["rollen"]["dev"].standaardwerkstroom, "dev")
        self.assertIsInstance(gegevens["medewerkers"][0], Medewerker)
        self.assertIsInstance(gegevens["roosters"]["R01"], Rooster)
        self.assertIsInstance(gegevens["percentages"]["P001"], Percentageverdeling)
        self.assertIsInstance(gegevens["toewijzingen"][0], Roostertoewijzing)
        self.assertIsInstance(gegevens["toewijzingen"][1], PercentageToewijzing)
        self.assertEqual(
            gegevens["afwezigheden"]["j001"][date(2026, 11, 3)],
            "4V",
        )
        self.assertEqual(gegevens["uren_per_storypoint"], 6.0)
        self.assertEqual(
            gegevens["agile_instellingen"],
            [{
                "type": "DagStart",
                "ma": True,
                "di": True,
                "wo": False,
                "do": True,
                "vr": False,
                "duur": 0.5,
            }],
        )


    def test_rol_zonder_sprintwerk_heeft_geen_standaardwerkstroom(self):
        data = voorbeeld()
        data["rollen"][0]["doet_sprintwerk"] = False

        gegevens = laad_contract(json.dumps(data))

        self.assertIsNone(gegevens["rollen"]["dev"].standaardwerkstroom)

    def test_doet_sprintwerk_moet_een_boolean_zijn(self):
        data = voorbeeld()
        data["rollen"][0]["doet_sprintwerk"] = "ja"

        with self.assertRaises(ContractValidatieFout) as context:
            laad_contract(json.dumps(data))

        self.assertEqual(context.exception.foutcode, "ONGELDIGE_WAARDE")

    def test_agile_dagen_moeten_booleans_zijn(self):
        data = voorbeeld()
        data["agile_instellingen"][0]["wo"] = "Nee"

        with self.assertRaises(ContractValidatieFout) as context:
            laad_contract(json.dumps(data))

        self.assertEqual(context.exception.foutcode, "ONGELDIGE_AGILE_DAG")
        self.assertEqual(
            context.exception.gegevenspad,
            "$.agile_instellingen[0].wo",
        )

    def test_agile_dagveld_is_verplicht(self):
        data = voorbeeld()
        del data["agile_instellingen"][0]["vr"]

        with self.assertRaises(ContractValidatieFout) as context:
            laad_contract(json.dumps(data))

        self.assertEqual(context.exception.foutcode, "ONGELDIGE_AGILE_DAG")
        self.assertEqual(
            context.exception.gegevenspad,
            "$.agile_instellingen[0].vr",
        )

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
        data["contract"]["versie"] = "2.0"

        with self.assertRaises(ContractValidatieFout) as context:
            laad_contract(json.dumps(data))

        self.assertEqual(
            context.exception.foutcode,
            "CONTRACTVERSIE_NIET_ONDERSTEUND",
        )

    def test_ontbrekende_roostertoewijzing_wordt_doorgelaten_naar_sprintvalidatie(self):
        data = voorbeeld()
        data["toewijzingen"] = [
            t for t in data["toewijzingen"] if t["type"] != "Rooster"
        ]

        gegevens = laad_contract(json.dumps(data))

        self.assertEqual(len(gegevens["toewijzingen"]), 1)
        self.assertIsInstance(gegevens["toewijzingen"][0], PercentageToewijzing)

    def test_roosterovergang_over_weekend_is_geldig(self):
        data = voorbeeld()
        data["instellingen"]["datum_eerste_sprint"] = "2026-10-19"
        data["instellingen"]["standaard_sprintduur"] = 2

        data["roosters"].append({
            "rooster_id": "R02",
            "cyclus_weken": 1,
            "uren_per_week": [[8, 8, 8, 8, 4]],
        })

        data["toewijzingen"][0]["geldig_tm"] = "2026-10-23"
        data["toewijzingen"].append({
            "userid": "j001",
            "type": "Rooster",
            "toewijzing_id": "R02",
            "geldig_vanaf": "2026-10-26",
            "geldig_tm": None,
        })

        gegevens = laad_contract(json.dumps(data))

        self.assertEqual(len(gegevens["toewijzingen"]), 3)

    def test_gat_in_roostertoewijzingen_wordt_doorgelaten(self):
        data = voorbeeld()
        data["instellingen"]["datum_eerste_sprint"] = "2026-10-19"
        data["instellingen"]["standaard_sprintduur"] = 2

        data["roosters"].append({
            "rooster_id": "R02",
            "cyclus_weken": 1,
            "uren_per_week": [[8, 8, 8, 8, 4]],
        })

        data["toewijzingen"][0]["geldig_tm"] = "2026-10-23"
        data["toewijzingen"].append({
            "userid": "j001",
            "type": "Rooster",
            "toewijzing_id": "R02",
            "geldig_vanaf": "2026-10-27",
            "geldig_tm": None,
        })

        gegevens = laad_contract(json.dumps(data))

        self.assertEqual(len(gegevens["toewijzingen"]), 3)

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

    def test_afwezigheidscode_wordt_bewaard_voor_sprintvalidatie(self):
        data = voorbeeld()
        data["afwezigheden"][0]["code"] = "X"

        gegevens = laad_contract(json.dumps(data))

        self.assertEqual(gegevens["afwezigheid_records"][0]["code"], "X")

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
