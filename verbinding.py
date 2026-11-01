import uno
import subprocess
import time

def verbind_met_calc():
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )
    url = "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
    try:
        ctx = resolver.resolve(url)
    except Exception:
        programma = r"C:\Program Files\LibreOffice\program\soffice.exe"
        subprocess.Popen([
            programma,
            "--accept=socket,host=127.0.0.1,port=2002;urp;StarOffice.ServiceManager",
            "--norestore",
            "--nodefault"
        ])
        for poging in range(20):
            time.sleep(0.5)
            try:
                ctx = resolver.resolve(url)
                break
            except Exception:
                pass
        else:
            raise ConnectionError(
                "LibreOffice kon niet worden gestart of bereikt."
            )
    desktop = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", ctx
    )
    return ctx, desktop