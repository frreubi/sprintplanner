import uno
import json
import applicatie

def verbind():
    lokaal = uno.getComponentContext()

    resolver = lokaal.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver",
        lokaal
    )

    return resolver.resolve(
        "uno:socket,host=127.0.0.1,port=2002;urp;document"
    )


if __name__ == "__main__":
    document = verbind()

    provider = document.getScriptProvider()

    script = provider.getScript(
        "vnd.sun.star.script:sprintplanner.py$lever_contractbericht"
        "?language=Python&location=user"
    )

    resultaat = script.invoke((), (), ())
    contract_json = resultaat[0]
    resultaten = applicatie.verwerk_contract(contract_json)

    print(contract_json)