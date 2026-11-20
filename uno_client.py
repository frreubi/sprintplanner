import sys
import uno


MACRO_PAD = "vnd.sun.star.script:sprintplanner.py${}?language=Python&location=user"


def verbind():
    lokaal = uno.getComponentContext()

    resolver = lokaal.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver",
        lokaal,
    )

    return resolver.resolve(
        "uno:socket,host=127.0.0.1,port=2002;urp;document"
    )


def voer_macro_uit(macro_naam, *argumenten):
    document = verbind()
    provider = document.getScriptProvider()

    script_url = MACRO_PAD.format(macro_naam)
    script = provider.getScript(script_url)

    resultaat = script.invoke(argumenten, (), ())
    return resultaat[0]


def haal_contractbericht_op():
    return voer_macro_uit("lever_contractbericht")


def sla_beheeronderdeel_op(onderdeel, gegevens_json):
    return voer_macro_uit(
        "sla_beheeronderdeel_op",
        onderdeel,
        gegevens_json,
    )


def main():
    if len(sys.argv) == 1:
        print(haal_contractbericht_op())
        return

    if len(sys.argv) == 3 and sys.argv[1] == "opslaan":
        onderdeel = sys.argv[2]
        gegevens_json = sys.stdin.read()
        if not gegevens_json.strip():
            raise ValueError("Geen beheergegevens ontvangen via standaardinvoer.")

        print(sla_beheeronderdeel_op(onderdeel, gegevens_json))
        return

    raise ValueError(
        "Gebruik: uno_client.py [opslaan <onderdeel>]"
    )


if __name__ == "__main__":
    main()
