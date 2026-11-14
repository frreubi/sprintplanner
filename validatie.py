import re
from datetime import timedelta

from berekeningen import bereken_feestdagen
from toewijzingen import Roostertoewijzing, PercentageToewijzing


PATROON_AFWEZIGHEIDSCODE = re.compile(r"^(?:[1-9][0-9]*)?[VBCZ]$")


def valideer_sprintgegevens(
    medewerkers,
    startdatum,
    einddatum,
    afwezigheid_records,
    toewijzingen,
):
    fouten = []

    if einddatum < startdatum:
        return ["De einddatum ligt vóór de begindatum."]

    feestdagen = set()
    for jaar in range(startdatum.year, einddatum.year + 1):
        feestdagen.update(bereken_feestdagen(jaar))

    records_per_dag = {}
    for record in afwezigheid_records:
        sleutel = (record["userid"], record["datum"])
        records_per_dag.setdefault(sleutel, []).append(record)

    for medewerker in medewerkers:
        eerste_dag = max(startdatum, medewerker.startdatum)
        laatste_dag = min(
            einddatum,
            medewerker.einddatum
            if medewerker.einddatum is not None
            else einddatum,
        )

        dag = eerste_dag
        while dag <= laatste_dag:
            if dag not in feestdagen:
                roosters = [
                    toewijzing
                    for toewijzing in toewijzingen
                    if isinstance(toewijzing, Roostertoewijzing)
                    and toewijzing.medewerker is medewerker
                    and toewijzing.geldt_op(dag)
                ]

                if dag.weekday() < 5:
                    if not roosters:
                        fouten.append(
                            f"Medewerker {medewerker.userid} heeft op "
                            f"{dag.isoformat()} geen rooster toegewezen."
                        )
                    elif len(roosters) > 1:
                        fouten.append(
                            f"Medewerker {medewerker.userid} heeft op "
                            f"{dag.isoformat()} meerdere roosters toegewezen."
                        )

                percentages = [
                    toewijzing
                    for toewijzing in toewijzingen
                    if isinstance(toewijzing, PercentageToewijzing)
                    and toewijzing.medewerker is medewerker
                    and toewijzing.geldt_op(dag)
                ]
                if len(percentages) > 1:
                    fouten.append(
                        f"Medewerker {medewerker.userid} heeft op "
                        f"{dag.isoformat()} meerdere percentage-toewijzingen."
                    )

                records = records_per_dag.get(
                    (medewerker.userid, dag), []
                )

                if len(records) > 1:
                    fouten.append(
                        f"Medewerker {medewerker.userid} heeft meer dan "
                        f"één afwezigheidsregistratie op {dag.isoformat()}."
                    )

                for record in records:
                    code = record["code"].strip().upper()
                    if not PATROON_AFWEZIGHEIDSCODE.fullmatch(code):
                        fouten.append(
                            f"Ongeldige afwezigheidscode {code!r} voor "
                            f"medewerker {medewerker.userid} op "
                            f"{dag.isoformat()}."
                        )

            dag += timedelta(days=1)

    return fouten
