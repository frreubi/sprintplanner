import json
import subprocess
from pathlib import Path

LO_PYTHON = Path(
    r"C:\Program Files\LibreOffice\program\python.exe"
)

PROJECTMAP = Path(__file__).parent
UNO_CLIENT = PROJECTMAP / "uno_client.py"


def _voer_uno_client_uit(*argumenten, invoer=None):
    resultaat = subprocess.run(
        [str(LO_PYTHON), str(UNO_CLIENT), *argumenten],
        input=invoer,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    if resultaat.returncode != 0:
        details = resultaat.stderr.strip() or resultaat.stdout.strip()
        raise RuntimeError(
            "De communicatie met LibreOffice is mislukt.\n"
            f"Exitcode: {resultaat.returncode}\n"
            f"{details or 'Geen foutmelding ontvangen.'}"
        )

    antwoord = resultaat.stdout.strip()
    if not antwoord:
        raise RuntimeError(
            "LibreOffice heeft geen antwoord teruggegeven."
        )

    return antwoord


def haal_contractbericht_op():
    return _voer_uno_client_uit()


def haal_sprintresultaten_op():
    from applicatie import verwerk_contract

    bericht = haal_contractbericht_op()
    return verwerk_contract(bericht)


def sla_beheeronderdeel_op(onderdeel, gegevens):
    gegevens_json = json.dumps(gegevens, ensure_ascii=False)
    antwoord = _voer_uno_client_uit(
        "opslaan",
        onderdeel,
        invoer=gegevens_json,
    )

    try:
        resultaat = json.loads(antwoord)
    except json.JSONDecodeError as fout:
        raise RuntimeError(
            "LibreOffice gaf een ongeldig opslagantwoord terug: "
            f"{antwoord}"
        ) from fout

    if not isinstance(resultaat, dict) or not resultaat.get("gelukt"):
        melding = (
            resultaat.get("fout", "Onbekende opslagfout.")
            if isinstance(resultaat, dict)
            else "Ongeldig opslagantwoord ontvangen."
        )
        raise RuntimeError(
            f"Opslaan van {onderdeel} is mislukt: {melding}"
        )

    return resultaat
