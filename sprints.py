from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class Sprint:
    sprintID: int
    begindatum: date
    einddatum: date


def zoek_sprint(datum, sprints):
    gevonden = [
        sprint for sprint in sprints
        if (
            sprint.begindatum <= datum <= sprint.einddatum
            if isinstance(sprint, Sprint)
            else sprint["begindatum"] <= datum <= sprint["einddatum"]
        )
    ]

    if len(gevonden) > 1:
        raise ValueError("Sprints overlappen op deze datum.")

    if not gevonden:
        return None

    return gevonden[0]
