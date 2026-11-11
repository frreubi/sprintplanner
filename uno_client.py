import uno


def verbind():
    lokaal = uno.getComponentContext()

    resolver = lokaal.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver",
        lokaal,
    )

    return resolver.resolve(
        "uno:socket,host=127.0.0.1,port=2002;urp;document"
    )


def haal_contractbericht_op():
    document = verbind()
    provider = document.getScriptProvider()

    script = provider.getScript(
        "vnd.sun.star.script:sprintplanner.py$lever_contractbericht"
        "?language=Python&location=user"
    )

    resultaat = script.invoke((), (), ())
    return resultaat[0]


if __name__ == "__main__":
    print(haal_contractbericht_op())
