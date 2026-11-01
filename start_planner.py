
import subprocess
from pathlib import Path

mapnaam = Path(__file__).parent
programma = r"C:\Program Files\LibreOffice\program\soffice.exe"
bestand = mapnaam / "Verlof en Sprints 2026.ods"

subprocess.Popen([
    programma,
    "--accept=socket,host=127.0.0.1,port=2002;urp;StarOffice.ServiceManager",
    "--norestore",
    "--nodefault",
    str(bestand)
])
input("Launcher klaar. Druk op Enter om af te sluiten...")