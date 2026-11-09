import json
import os
import subprocess
from pathlib import Path

from berekeningen import bereken_sprintresultaten
from contract import laad_contract


PROJECTMAP = Path(
    r"C:\Users\frreu\Documents\LibreOfficeProject\Sprintplanner"
)

PYTHON = Path(
    r"C:\Users\frreu\AppData\Local\Python\pythoncore-3.15-64\python.exe"
)

LO_PYTHON = Path(
    r"C:\Program Files\LibreOffice\program\python.exe"
)

UNO_CLIENT = PROJECTMAP / "test_uno_client.py"

def haal_contractbericht_op():
    resultaat = subprocess.run(
        [str(LO_PYTHON), str(UNO_CLIENT)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True
    )

    return resultaat.stdout

def verwerk_contract(bericht):
    gegevens = laad_contract(bericht)
    sprintresultaten = []

    for sprint in gegevens["sprints"]:
        netto_uren = bereken_sprintresultaten(
            gegevens["medewerkers"],
            sprint.begindatum,
            sprint.einddatum,
            gegevens["afwezigheden"],
            gegevens["toewijzingen"],
            gegevens["agile_instellingen"],
            gegevens["uren_per_storypoint"],
        )

        sprintresultaten.append({
            "naam": sprint.naam,
            "begindatum": sprint.begindatum.isoformat(),
            "einddatum": sprint.einddatum.isoformat(),
            "agile_instellingen": gegevens["agile_instellingen"],
            "netto_uren": netto_uren,
        })

    return sprintresultaten

def haal_sprintgegevens_op():
    bericht = haal_contractbericht_op()
    return verwerk_contract(bericht)

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
