import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import date
from rooster import Rooster


def test_tweewekelijks_rooster():
    rooster = Rooster(
        "R001",
        2,
        [
            [7, 7, 7, 8, 8],
            [8, 8, 8, 8, 7],
        ],
  )

    assert rooster.uren_op(date(2026, 10, 19)) == 7
    assert rooster.uren_op(date(2026, 10, 26)) == 8
    assert rooster.uren_op(date(2026, 10, 24)) == 0



def test_eenwekelijks_rooster():
    rooster = Rooster(
        "R003",
        1,
        [[8, 8, 8, 8, 0]],
    )
    assert rooster.uren_op(date(2026, 10, 19)) == 8
    assert rooster.uren_op(date(2026, 10, 26)) == 8


def test_ongeldige_cyclus():
    try:
        Rooster("R004", 3, [[8, 8, 8, 8, 8]])
    except ValueError:
        return
    raise AssertionError("Een cyclus van 3 weken had afgewezen moeten worden")



test_tweewekelijks_rooster()
test_eenwekelijks_rooster()
test_ongeldige_cyclus()
print("Alle tests geslaagd.")
