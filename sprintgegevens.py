from pathlib import Path
import subprocess

LO_PYTHON = Path(
    r"C:\Program Files\LibreOffice\program\python.exe"
)

PROJECTMAP = Path(__file__).parent
UNO_CLIENT = PROJECTMAP / "uno_client.py"


def haal_contractbericht_op():
    resultaat = subprocess.run(
        [str(LO_PYTHON), str(UNO_CLIENT)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    if resultaat.returncode != 0:
        details = resultaat.stderr.strip() or resultaat.stdout.strip()
        raise RuntimeError(
            "Ophalen van het contractbericht via LibreOffice is mislukt.\n"
            f"Exitcode: {resultaat.returncode}\n"
            f"{details or 'Geen foutmelding ontvangen.'}"
        )

    if not resultaat.stdout.strip():
        raise RuntimeError(
            "LibreOffice heeft geen contractbericht teruggegeven."
        )

    return resultaat.stdout


def haal_sprintresultaten_op():
    from applicatie import verwerk_contract

    bericht = haal_contractbericht_op()
    return verwerk_contract(bericht)
