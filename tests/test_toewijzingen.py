import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import date
from medewerker import Medewerker
from rooster import Rooster
from toewijzingen import Roostertoewijzing

rooster = Rooster("R001", 1, [[8, 8, 8, 8, 4]])
medewerker = Medewerker(
    "p002", "Petra", "", "Jansen", "ops"
)
toewijzing = Roostertoewijzing(
    medewerker, rooster, date(2026, 1, 5), date(2026, 1, 9)
)

# De begin- en einddatum tellen mee.
assert toewijzing.geldt_op(date(2026, 1, 5))
assert toewijzing.geldt_op(date(2026, 1, 9))

# Buiten de geldigheidsperiode geldt de toewijzing niet.
assert not toewijzing.geldt_op(date(2026, 1, 4))
assert not toewijzing.geldt_op(date(2026, 1, 10))

# Zonder einddatum blijft de toewijzing geldig.
doorlopend = Roostertoewijzing(
    medewerker, rooster, date(2026, 1, 5)
)
assert doorlopend.geldt_op(date(2026, 12, 31))

# Een einddatum vóór de begindatum moet worden afgewezen.
try:
    Roostertoewijzing(
        medewerker, rooster, date(2026, 1, 9), date(2026, 1, 5)
    )
    raise AssertionError("Ongeldige datums zijn niet afgewezen")
except ValueError:
    pass

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

print("Alle tests voor Roostertoewijzing geslaagd.")

from toewijzingen import zoek_toewijzing

# Twee opeenvolgende roosters voor Petra.
rooster_nieuw = Rooster("R002", 1, [[9, 9, 9, 4, 0]])
eerste = Roostertoewijzing(
    medewerker, rooster, date(2026, 1, 5), date(2026, 1, 9)
)
tweede = Roostertoewijzing(
    medewerker, rooster_nieuw, date(2026, 1, 12)
)
toewijzingen = [eerste, tweede]

# De juiste toewijzing wordt gevonden.
assert zoek_toewijzing(
    medewerker, date(2026, 1, 7), toewijzingen
) is eerste
assert zoek_toewijzing(
    medewerker, date(2026, 1, 12), toewijzingen
) is tweede

# Geen toewijzing op deze datum.
try:
    zoek_toewijzing(medewerker, date(2026, 1, 4), toewijzingen)
    raise AssertionError("Ontbrekende toewijzing is niet afgewezen")
except ValueError as fout:
    assert "Geen roostertoewijzing" in str(fout)

# Twee gelijktijdig geldige toewijzingen moeten een fout geven.
overlap = Roostertoewijzing(
    medewerker, rooster_nieuw, date(2026, 1, 8)
)
try:
    zoek_toewijzing(
        medewerker, date(2026, 1, 8), [eerste, overlap]
    )
    raise AssertionError("Overlappende toewijzingen zijn niet afgewezen")
except ValueError as fout:
    assert "Meerdere roostertoewijzingen" in str(fout)

print("Alle tests voor zoek_toewijzing geslaagd.")