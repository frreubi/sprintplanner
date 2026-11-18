import json
import os
import subprocess
from pathlib import Path

from berekeningen import bereken_sprintresultaten
from contract import laad_contract
from validatie import valideer_sprintgegevens


PROJECTMAP = Path(
    r"C:\Users\frreu\Documents\LibreOfficeProject\Sprintplanner"
)

PYTHON = Path(
    r"C:\Users\frreu\AppData\Local\Python\pythoncore-3.15-64\python.exe"
)


def verwerk_contract(bericht):
    gegevens = laad_contract(bericht)
    sprintresultaten = []

    for sprint in gegevens["sprints"]:
        fouten = valideer_sprintgegevens(
            gegevens["medewerkers"],
            sprint.begindatum,
            sprint.einddatum,
            gegevens["afwezigheid_records"],
            gegevens["toewijzingen"],
        )

        netto_uren = []
        if not fouten:
            netto_uren = bereken_sprintresultaten(
                gegevens["medewerkers"],
                sprint.begindatum,
                sprint.einddatum,
                gegevens["afwezigheden"],
                gegevens["toewijzingen"],
                gegevens["agile_instellingen"],
                gegevens["uren_per_storypoint"],
                gegevens["rollen"],
            )

        sprintresultaten.append({
            "sprintID": sprint.sprintID,
            "begindatum": sprint.begindatum.isoformat(),
            "einddatum": sprint.einddatum.isoformat(),
            "agile_instellingen": gegevens["agile_instellingen"],
            "netto_uren": netto_uren,
            "fouten": fouten,
        })

    return sprintresultaten


def start(bericht):
    sprintresultaten = verwerk_contract(bericht)

    jsonbestand = PROJECTMAP / "sprints.json"
    jsonbestand.write_text(
        json.dumps(sprintresultaten, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    logbestand = PROJECTMAP / "logs" / "sprintinfo_fout.txt"
    omgeving = os.environ.copy()
    omgeving.pop("PYTHONHOME", None)
    omgeving.pop("PYTHONPATH", None)

    with logbestand.open("w", encoding="utf-8") as log:
        subprocess.Popen(
            [
                str(PYTHON),
                str(PROJECTMAP / "sprintinfo.py"),
                str(jsonbestand),
            ],
            stdout=log,
            stderr=log,
            env=omgeving,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
