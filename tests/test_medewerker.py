import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import date
from medewerker import Medewerker, controleer_rolpercentages

def test_geldige_medewerker():
    m = Medewerker("j001", "Jan", "van der", "Berg", "dev")
    assert m.naam == "Jan van der Berg"
    assert m.einddatum is None

def test_rolpercentages_en_controle():
    m = Medewerker("j001", "Jan", "", "Berg", "dev", 60, 20, 20)
    assert (m.dev, m.ops, m.func) == (60, 20, 20)
    assert controleer_rolpercentages([m]) == []


def test_waarschuwing_rolpercentages_niet_100():
    m = Medewerker("j001", "Jan", "", "Berg", "dev", 60, 20, 10)
    waarschuwingen = controleer_rolpercentages([m])
    assert len(waarschuwingen) == 1
    assert "Jan Berg" in waarschuwingen[0]
    assert "90%" in waarschuwingen[0]


def test_ongeldig_rolpercentage():
    try:
        Medewerker("j001", "Jan", "", "Berg", "dev", 101, 0, 0)
    except ValueError:
        return
    raise AssertionError("Een percentage boven 100 had afgewezen moeten worden")


def test_leeg_userid():
    try:
        Medewerker("", "Jan", "van der", "Berg", "dev")
    except ValueError:
        return
    raise AssertionError("Een leeg userid had afgewezen moeten worden")

def test_ongeldige_wijziging_voornaam():
    m = Medewerker("j001", "Jan", "van der", "Berg", "dev")
    try:
        m.voornaam = ""
    except ValueError:
        return
    raise AssertionError("Een lege voornaam had afgewezen moeten worden")

def test_ongeldig_tussenvoegsel():
    m = Medewerker("j001", "Jan", "van der", "Berg", "dev")
    try:
        m.tussenvoegsel = None
    except ValueError:
        return
    raise AssertionError("Een niet-tekstueel tussenvoegsel had afgewezen moeten worden")

def test_ongeldige_wijziging_achternaam():
    m = Medewerker("j001", "Jan", "van der", "Berg", "dev")
    try:
        m.achternaam = ""
    except ValueError:
        return
    raise AssertionError("Een lege achternaam had afgewezen moeten worden")

def test_ongeldige_rol():
    try:
        Medewerker("j001", "Jan", "van der", "Berg", "manager")
    except ValueError:
        return
    raise AssertionError("Een ongeldige rol had afgewezen moeten worden")

def test_rol_wordt_kleine_letters():
    m = Medewerker("j001", "Jan", "van der", "Berg", "DEV")
    assert m.rol == "dev"

def test_einddatum_medewerker():
    m = Medewerker(
        "p002", "Petra", "", "Jansen", "ops",
        einddatum=date(2030, 10, 15)
    )
    assert m.einddatum == date(2030, 10, 15)

def test_einddatum_onbekend():
    m = Medewerker("p002", "Petra", "", "Jansen", "ops")
    assert m.einddatum is None

def test_ongeldige_einddatum():
    try:
        Medewerker(
            "p002", "Petra", "", "Jansen", "ops",
            einddatum="15-10-2030"
        )
    except ValueError:
        return
    raise AssertionError("Een tekstuele einddatum had afgewezen moeten worden")

def test_ongeldige_beheerder():
    try:
        Medewerker("j001", "Jan", "", "Berg", "dev", beheerder="ja")
    except ValueError:
        return
    raise AssertionError("Een ongeldige beheerderwaarde had afgewezen moeten worden")

def test_ongeldige_access_analist():
    try:
        Medewerker("j001", "Jan", "", "Berg", "dev", access_analist=1)
    except ValueError:
        return
    raise AssertionError("Een ongeldige access_analistwaarde had afgewezen moeten worden")

test_geldige_medewerker()
test_rolpercentages_en_controle()
test_waarschuwing_rolpercentages_niet_100()
test_ongeldig_rolpercentage()
test_leeg_userid()
test_ongeldige_wijziging_voornaam()
test_ongeldig_tussenvoegsel()
test_ongeldige_wijziging_achternaam()
test_ongeldige_rol()
test_rol_wordt_kleine_letters()
test_einddatum_medewerker()
test_einddatum_onbekend()
test_ongeldige_einddatum()
test_ongeldige_beheerder()
test_ongeldige_access_analist()
print("Alle tests voor Medewerker geslaagd.")
