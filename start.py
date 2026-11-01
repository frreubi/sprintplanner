import time
import traceback
from pathlib import Path
import uno

logbestand = Path(__file__).with_name("start.log")
logbestand.write_text("Nieuwe start.py gestart\n", encoding="utf-8")
print(logbestand.resolve())

def log(tekst):
    with logbestand.open("a", encoding="utf-8") as bestand:
        bestand.write(tekst + "\n")

try:
    log("Verbinding zoeken...")
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )
    url = "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"

    for poging in range(20):
        try:
            ctx = resolver.resolve(url)
            desktop = ctx.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", ctx
            )
            log("UNO-verbinding geslaagd.")
            break
        except Exception:
            time.sleep(0.5)
    else:
        raise ConnectionError("Na 10 seconden geen UNO-verbinding.")

except Exception:
    log(traceback.format_exc())