
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import os

mapnaam = Path(__file__).parent
bron = mapnaam / "Sprintplanner_demo.ods"
doel = mapnaam / "Sprintplanner_demo_testselect.ods"
tijdelijk = mapnaam / "content_test.xml"

NS_TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
NS_LOEXT = "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0"

ET.register_namespace("table", NS_TABLE)
ET.register_namespace("loext", NS_LOEXT)

with ZipFile(bron, "r") as origineel:
    xml = origineel.read("content.xml")
    root = ET.fromstring(xml)

    gevonden = False
    for blad in root.iter(f"{{{NS_TABLE}}}table"):
        if blad.get(f"{{{NS_TABLE}}}name") == "Blad2":
            beveiliging = blad.find(f"{{{NS_LOEXT}}}table-protection")
            if beveiliging is None:
                beveiliging = ET.SubElement(
                    blad, f"{{{NS_LOEXT}}}table-protection"
                )
            beveiliging.set(
                f"{{{NS_LOEXT}}}select-protected-cells", "false"
            )
            beveiliging.set(
                f"{{{NS_LOEXT}}}select-unprotected-cells", "true"
            )
            gevonden = True
            break

    if not gevonden:
        raise RuntimeError("Blad2 niet gevonden in content.xml")

    ET.ElementTree(root).write(
        tijdelijk, encoding="UTF-8", xml_declaration=True
    )

    with ZipFile(doel, "w", ZIP_DEFLATED) as nieuw:
        for item in origineel.infolist():
            if item.filename == "content.xml":
                nieuw.write(tijdelijk, "content.xml")
            else:
                nieuw.writestr(item, origineel.read(item.filename))

tijdelijk.unlink(missing_ok=True)
print(f"Testkopie gemaakt: {doel}")
print("Selectie-instellingen aangepast voor Blad2.")
