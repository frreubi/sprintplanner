
import uno

lokaal = uno.getComponentContext()
resolver = lokaal.ServiceManager.createInstanceWithContext(
    "com.sun.star.bridge.UnoUrlResolver", lokaal
)
context = resolver.resolve(
    "uno:socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext"
)
desktop = context.ServiceManager.createInstanceWithContext(
    "com.sun.star.frame.Desktop", context
)

documenten = desktop.getComponents().createEnumeration()
print("Geopende documenten:")

while documenten.hasMoreElements():
    doc = documenten.nextElement()
    print(doc.Title, "|", doc.URL)
