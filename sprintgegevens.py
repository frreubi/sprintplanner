from pathlib import Path
import subprocess

LO_PYTHON = Path(
    r"C:\Program Files\LibreOffice\program\python.exe"
)

PROJECTMAP = Path(__file__).parent
UNO_CLIENT = PROJECTMAP / "test_uno_client.py"


def haal_contractbericht_op():
    resultaat = subprocess.run(
        [str(LO_PYTHON), str(UNO_CLIENT)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return resultaat.stdout

def haal_sprintresultaten_op():
    from applicatie import verwerk_contract

    bericht = haal_contractbericht_op()
    return verwerk_contract(bericht)