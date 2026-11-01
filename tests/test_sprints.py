import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import date
from sprints import zoek_sprint

sprints = [
    {
        "naam": "2026-44",
        "begindatum": date(2026, 10, 26),
        "einddatum": date(2026, 11, 13),
    }
]

assert zoek_sprint(date(2026, 11, 2), sprints) == sprints[0]
assert zoek_sprint(date(2026, 11, 14), sprints) is None

overlap = sprints + [
    {
        "naam": "2026-45",
        "begindatum": date(2026, 11, 10),
        "einddatum": date(2026, 11, 20),
    }
]

try:
    zoek_sprint(date(2026, 11, 12), overlap)
    raise AssertionError("Overlappingen zijn niet ontdekt.")
except ValueError:
    pass

print("Tests geslaagd.")