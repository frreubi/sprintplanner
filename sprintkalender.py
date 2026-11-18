from datetime import date, timedelta

from sprints import Sprint


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