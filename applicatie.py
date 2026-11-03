import json
import os
import subprocess
from pathlib import Path
from berekeningen import bereken_sprintresultaten


PROJECTMAP = Path(
    r"C:\Users\frreu\Documents\LibreOfficeProject\Sprintplanner"
)

PYTHON = Path(
    r"C:\Users\frreu\AppData\Local\Python\pythoncore-3.15-64\python.exe"
)


def start(gegevens):
    sprintgegevens = gegevens["sprints"]
    medewerkers = gegevens["medewerkers"]
    toewijzingen = gegevens["toewijzingen"]
    afwezigheden = gegevens["afwezigheden"]
    agile_instellingen = gegevens["agile_instellingen"]

    for sprint in sprintgegevens:
        sprint["agile_instellingen"] = agile_instellingen

        sprint["netto_uren"] = bereken_sprintresultaten(
            medewerkers,
            sprint["begindatum"],
            sprint["einddatum"],
            afwezigheden,
            toewijzingen,
            agile_instellingen,
            gegevens["uren_per_storypoint"],
        )

        sprint["begindatum"] = sprint["begindatum"].isoformat()
        sprint["einddatum"] = sprint["einddatum"].isoformat()

    jsonbestand = PROJECTMAP / "sprints.json"
    jsonbestand.write_text(
        json.dumps(sprintgegevens, ensure_ascii=False, indent=2),
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