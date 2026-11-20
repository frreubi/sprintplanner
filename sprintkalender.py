from datetime import date, timedelta

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Domein.sprints import Sprint


def genereer_sprints(
    datum_eerste_sprint: date,
    sprintduur_weken: int,
) -> list[Sprint]:

    if sprintduur_weken < 1:
        raise ValueError("Sprintduur moet minimaal één week zijn.")

    sprints = []
    begindatum = datum_eerste_sprint
    sprintduur = timedelta(weeks=sprintduur_weken)
    einde_planningsjaar = date(datum_eerste_sprint.year, 12, 31)

    volgnummer = 1

    while begindatum <= einde_planningsjaar:
        einddatum = begindatum + sprintduur - timedelta(days=1)

        sprints.append(
            Sprint(
                sprintID=volgnummer,
                begindatum=begindatum,
                einddatum=einddatum,
            )
        )

        begindatum = einddatum + timedelta(days=1)
        volgnummer += 1

    return sprints
