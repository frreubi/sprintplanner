import uno
import time
import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path
from medewerker import Medewerker
from rooster import Rooster
from berekeningen import bereken_roosteruren
from berekeningen import bereken_feestdagen
from kalender import datums_roosterjaar, maandkoppen_roosterjaar
from verbinding import verbind_met_calc

# Maak verbinding met de bestaande LibreOffice-sessie.
ctx, desktop = verbind_met_calc()

rooster_r001 = Rooster("R001", 1, [[8, 8, 8, 8, 4]])
rooster_r002 = Rooster("R002", 1, [[8, 8, 8, 8, 0]])

medewerkers = [
    Medewerker("j001", "Jan", "van der", "Berg", "dev"),
    Medewerker("p002", "Petra", "", "Jansen", "ops"),
    Medewerker("a003", "Ahmed", "", "Bakker", "func"),
    Medewerker("frreu", "Roel", "", "Rigterink", "dev"),
]

WACHTWOORD = "@1Zihw001"
KLEUR_ONEVEN = 0xD8EAD5
KLEUR_EVEN = 0xB8D8B2
KLEUR_WEEK = 0xE8F2E5
KLEUR_RAND = 0x8BA66B
KLEUR_WEEKEND = 0xE6E6E6

def stel_selectie_in_ods(bestand, bladnaam):
    """Sta alleen selectie van ontgrendelde cellen toe in het gekozen werkblad."""
    ns_table = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    ns_loext = "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0"
    ET.register_namespace("table", ns_table)
    ET.register_namespace("loext", ns_loext)

    tijdelijk = bestand.with_name(bestand.stem + "_tijdelijk.ods")
    with zipfile.ZipFile(bestand, "r") as origineel:
        root = ET.fromstring(origineel.read("content.xml"))
        gevonden = False
        for blad_xml in root.iter(f"{{{ns_table}}}table"):
            if blad_xml.get(f"{{{ns_table}}}name") == bladnaam:
                beveiliging = blad_xml.find(f"{{{ns_loext}}}table-protection")
                if beveiliging is None:
                    beveiliging = ET.SubElement(
                        blad_xml, f"{{{ns_loext}}}table-protection"
                    )
                beveiliging.set(f"{{{ns_loext}}}select-protected-cells", "false")
                beveiliging.set(f"{{{ns_loext}}}select-unprotected-cells", "true")
                gevonden = True
                break
        if not gevonden:
            raise RuntimeError(f"Werkblad {bladnaam} niet gevonden in content.xml")

        xml_aangepast = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
        with zipfile.ZipFile(tijdelijk, "w", zipfile.ZIP_DEFLATED) as nieuw:
            for item in origineel.infolist():
                inhoud = xml_aangepast if item.filename == "content.xml" else origineel.read(item.filename)
                nieuw.writestr(item, inhoud)

    os.replace(tijdelijk, bestand)


def beveilig_kalender(blad, jaar, medewerkers, datums, eerste_kolom):
    # Vergrendel eerst het volledige gegenereerde kalendergebied.
    laatste_kolom = eerste_kolom + len(datums) - 1
    laatste_rij = 3 + len(medewerkers)
    bereik = blad.getCellRangeByPosition(
        0, 0, laatste_kolom, laatste_rij
    )
    beveiliging = bereik.CellProtection
    beveiliging.IsLocked = True
    bereik.CellProtection = beveiliging

    feestdagen = bereken_feestdagen(jaar)

    # Maak alleen werkdagen van het gekozen ISO-roosterjaar wijzigbaar.
    begin = None
    for index in range(len(datums) + 1):
        wijzigbaar = (
            index < len(datums)
            and datums[index].isocalendar().year == jaar
            and datums[index].weekday() < 5
            and datums[index] not in feestdagen
        )

        if wijzigbaar and begin is None:
            begin = index
        elif not wijzigbaar and begin is not None:
            invoercellen = blad.getCellRangeByPosition(
                eerste_kolom + begin, 4,
                eerste_kolom + index - 1, laatste_rij
            )
            beveiliging = invoercellen.CellProtection
            beveiliging.IsLocked = False
            invoercellen.CellProtection = beveiliging
            begin = None

    # Beveilig het blad met het wachtwoord uit de constante.
    blad.protect(WACHTWOORD)

def schrijf_kalender(blad, jaar, medewerkers):
    functie_start = time.perf_counter()
    if blad.isProtected():
        blad.unprotect(WACHTWOORD)
    t0 = functie_start

    def meet(onderdeel):
        nonlocal t0
        nu = time.perf_counter()
        print(f"Kalender - {onderdeel}: {nu - t0:.2f} sec")
        t0 = nu

    datums = datums_roosterjaar(jaar)
    feestdagen = bereken_feestdagen(jaar)
    maandkoppen = maandkoppen_roosterjaar(jaar)

    # Bepaal de eerste en laatste kolom van iedere ISO-week.
    weken = []
    for index, datum in enumerate(datums):
        week = datum.isocalendar().week
        if not weken or weken[-1][0] != week:
            weken.append([week, index, index])
        else:
            weken[-1][2] = index

    # Schrijf de medewerkersnamen en rollen in kolom A en B.
    gegevens = tuple(
        (medewerker.naam, medewerker.rol)
        for medewerker in medewerkers
    )
    bereik = blad.getCellRangeByPosition(0, 4, 1, 3 + len(medewerkers))
    bereik.setDataArray(gegevens)
    meet("medewerkers schrijven")

    eerste_kolom = 2  # Kolom C

    # Maak het kalendergebied leeg.
    bereik = blad.getCellRangeByPosition(
        eerste_kolom, 0, eerste_kolom + len(datums) - 1, 3
    )
    bereik.clearContents(1023)
    meet("kalendergebied leegmaken")

    # Schrijf de dagdatums als echte Calc-datums.
    datumcellen = blad.getCellRangeByPosition(
        eerste_kolom, 3, eerste_kolom + len(datums) - 1, 3
    )
    nuldatum = date(1899, 12, 30)
    datumcellen.setDataArray((
        tuple((datum - nuldatum).days for datum in datums),
    ))

    # Toon alleen het dagnummer.
    formats = doc.NumberFormats
    locale = blad.getCellRangeByName("A1").getPropertyValue("CharLocale")
    dagformaat = formats.queryKey("D", locale, True)
    if dagformaat == -1:
        dagformaat = formats.addNew("D", locale)
    datumcellen.NumberFormat = dagformaat
    meet("datums schrijven en formatteren")

    # Toon de weekdag boven iedere datum.
    weekdagen = ("ma", "di", "wo", "do", "vr", "za", "zo")
    weekdagcellen = blad.getCellRangeByPosition(
        eerste_kolom, 2, eerste_kolom + len(datums) - 1, 2
    )
    weekdagcellen.setDataArray((
        tuple(weekdagen[datum.weekday()] for datum in datums),
    ))
    meet("weekdagen schrijven")

    # Schrijf de maandkoppen en kleur de maandgebieden.
    for maandnaam, begin, einde in maandkoppen:
        kolom_begin = eerste_kolom + begin
        kolom_einde = eerste_kolom + einde
        maandnummer = datums[begin].month
        kleur = KLEUR_ONEVEN if maandnummer % 2 else KLEUR_EVEN

        maandbereik = blad.getCellRangeByPosition(
            kolom_begin, 0, kolom_einde, 3
        )
        maandbereik.CellBackColor = kleur

        kopcel = blad.getCellRangeByPosition(
            kolom_begin, 0, kolom_einde, 0
        )
        kopcel.merge(True)
        kopcel.getCellByPosition(0, 0).setString(maandnaam)
    meet("maandkoppen maken en kleuren")

    # Maak eerst alle weekkoppen samen.
    for weeknummer, begin, einde in weken:
        kolom_begin = eerste_kolom + begin
        kolom_einde = eerste_kolom + einde
        weekbereik = blad.getCellRangeByPosition(
            kolom_begin, 1, kolom_einde, 1
        )
        weekbereik.merge(True)
    meet("weekkoppen samenvoegen")

    # Geef de weeknummerregel in één keer dezelfde lichte groentint.
    weekregel = blad.getCellRangeByPosition(
        eerste_kolom, 1,
        eerste_kolom + len(datums) - 1, 1
    )
    weekregel.CellBackColor = KLEUR_WEEK
    meet("weekkoppen kleuren")

    # Schrijf de weekteksten in één keer, met tekst op de eerste cel per week.
    weekteksten = [""] * len(datums)
    for weeknummer, begin, einde in weken:
        weekteksten[begin] = f"Week {weeknummer}"
    weekregel.setDataArray((tuple(weekteksten),))
    meet("weeknummers als array schrijven")

    # Maak de dagkolommen smal.
    dagkolommen = blad.getCellRangeByPosition(
        eerste_kolom, 0,
        eerste_kolom + len(datums) - 1, 0
    )
    dagkolommen.Columns.Width = 650
    meet("kolombreedtes instellen")

    # Bijzonder verlof: cadeau-uurtje en brugdag.
    brugdag = next(dag for dag in feestdagen if dag.weekday() == 3) + timedelta(days=1)

    for index, datum in enumerate(datums):
        if datum.weekday() < 5:
            kolom = eerste_kolom + index
            for rij in range(4, 4 + len(medewerkers)):
                if datum == brugdag:
                    code = "B"
                elif datum.month == 12 and datum.day in (5, 24, 31):
                    code = "1B"
                else:
                    continue
                blad.getCellByPosition(kolom, rij).setString(code)

    # Centreer de kalenderinhoud.
    kalenderbereik = blad.getCellRangeByPosition(
        eerste_kolom, 0, eerste_kolom + len(datums) - 1, 3
    )
    kalenderbereik.setPropertyValue(
        "HoriJustify",
        uno.Enum("com.sun.star.table.CellHoriJustify", "CENTER")
    )
    meet("inhoud centreren")

    # Geef het kalendergebied dunne, legergroene randen.
    lijn = uno.createUnoStruct("com.sun.star.table.BorderLine2")
    lijn.Color = KLEUR_RAND
    lijn.LineWidth = 10
    randen = kalenderbereik.TableBorder2
    randen.TopLine = lijn
    randen.BottomLine = lijn
    randen.LeftLine = lijn
    randen.RightLine = lijn
    randen.HorizontalLine = lijn
    randen.VerticalLine = lijn
    randen.IsTopLineValid = True
    randen.IsBottomLineValid = True
    randen.IsLeftLineValid = True
    randen.IsRightLineValid = True
    randen.IsHorizontalLineValid = True
    randen.IsVerticalLineValid = True
    kalenderbereik.TableBorder2 = randen
    meet("randen instellen")

    # Stel de hoogte van de kopregels in.
    blad.Rows.getByIndex(0).Height = 500
    blad.Rows.getByIndex(1).Height = 450
    blad.Rows.getByIndex(2).Height = 350
    meet("rijhoogtes instellen")

    # Geef zaterdag en zondag een grijze achtergrond.
    for index, datum in enumerate(datums):
        kolom = eerste_kolom + index
        dagbereik = blad.getCellRangeByPosition(
            kolom, 4, kolom, 3 + len(medewerkers)
        )
        if datum.weekday() >= 5:
            dagbereik.CellBackColor = KLEUR_WEEKEND
        if datum in feestdagen:
            dagbereik.CellBackColor = 0xFF00FF
    meet("weekendkleuring")


    beveilig_kalender(blad, jaar, medewerkers, datums, eerste_kolom)
    print(f"Kalender - TOTAAL: {time.perf_counter() - functie_start:.2f} sec")


def maak_knop(doc, blad, naam, tekst, cel_bovenlinks, cel_onderrechts):
    formulieren = blad.DrawPage.Forms
    if formulieren.getCount() == 0:
        formulier = doc.createInstance(
            "com.sun.star.form.component.Form"
        )
        formulieren.insertByName("Formulier", formulier)
    else:
        formulier = formulieren.getByIndex(0)

    # Verwijder de bestaande knop met dezelfde naam.
    if formulier.hasByName(naam):
        formulier.removeByName(naam)
    for i in range(blad.DrawPage.getCount() - 1, -1, -1):
        vorm_bestaand = blad.DrawPage.getByIndex(i)
        try:
            if vorm_bestaand.Control.Name == naam:
                blad.DrawPage.remove(vorm_bestaand)
        except AttributeError:
            pass

    knop = doc.createInstance(
        "com.sun.star.form.component.CommandButton"
    )
    knop.Name = naam
    knop.Label = tekst
    formulier.insertByName(naam, knop)
    
    gebeurtenis = uno.createUnoStruct(
        "com.sun.star.script.ScriptEventDescriptor"
    )
    gebeurtenis.ListenerType = "com.sun.star.awt.XActionListener"
    gebeurtenis.EventMethod = "actionPerformed"
    gebeurtenis.ScriptType = "Python"
    gebeurtenis.ScriptCode = (
        f"vnd.sun.star.script:sprintplanner.py${'toon_sprintinfo' if naam == 'knopSprintinfo' else 'beheer'}"
        "?language=Python&location=user"
    )
    formulier.registerScriptEvent(
        formulier.getCount() - 1, gebeurtenis
    )    

    begin = blad.getCellRangeByName(cel_bovenlinks).getRangeAddress()
    x = sum(blad.Columns.getByIndex(i).Width for i in range(begin.StartColumn))
    y = sum(blad.Rows.getByIndex(i).Height for i in range(begin.StartRow))

    # Compact formaat met wat ruimte vanaf de hoek.
    positie = uno.createUnoStruct("com.sun.star.awt.Point")
    positie.X = x + 500
    positie.Y = y + 100 if naam == "knopSprintinfo" else y

    grootte = uno.createUnoStruct("com.sun.star.awt.Size")
    grootte.Width = 2500
    grootte.Height = 600

    vorm = doc.createInstance(
        "com.sun.star.drawing.ControlShape"
    )
    vorm.setControl(knop)
    vorm.Position = positie
    vorm.Size = grootte
    blad.DrawPage.add(vorm)


# Zoek de demowerkmap in de bestaande UNO-sessie.
bestand = r"C:\Users\frreu\Documents\LibreOfficeProject\Sprintplanner\Verlof en Sprints 2026.ods"
url = uno.systemPathToFileUrl(bestand)
doc = None

for component in desktop.getComponents().createEnumeration():
    if component.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
        if component.URL == url:
            doc = component
            break

# Open de werkmap alleen als deze nog niet geopend is.
if doc is None:
    doc = desktop.loadComponentFromURL(url, "_blank", 0, ())

if doc is None:
    print("Het document kon niet worden geopend.")
else:
    print("Werkmap gebruikt:", doc.Title)
    kalenderblad = doc.Sheets.getByName("Afwezigheid")
    schrijf_kalender(kalenderblad, 2026, medewerkers)
    print("Kalenderfunctie klaar")
    doc.calculateAll()
    print("Kalender geschreven naar Afwezigheid.")

    maak_knop(doc, kalenderblad, "knopSprintinfo", "Sprintinfo", "A1", "B2")
    maak_knop(doc, kalenderblad, "knopBeheer", "Beheer", "A3", "B4")
    print("Knoppen gemaakt op Afwezigheid.")

    doc.store()
    # doc.close(True)

    # pad = Path(bestand)
    # stel_selectie_in_ods(pad, "Afwezigheid")

    # doc = desktop.loadComponentFromURL(url, "_blank", 0, ())
    # if doc is None:
    #     raise RuntimeError("Werkmap kon niet opnieuw worden geopend.")

    # kalenderblad = doc.Sheets.getByName("Afwezigheid")
    # print("Vormen na opnieuw openen:", kalenderblad.DrawPage.getCount())
    #doc = desktop.loadComponentFromURL(url, "_blank", 0, ())
    #if doc is None:
    #    raise RuntimeError("De werkmap kon na het instellen van de selectie niet opnieuw worden geopend.")
    #print("Beveiliging ingesteld: alleen ontgrendelde cellen zijn selecteerbaar.")
    #doc.store()
    #doc.close(True)
    #pad = Path(bestand)
    #stel_selectie_in_ods(pad, "Afwezigheid")
    #doc = desktop.loadComponentFromURL(url, "_blank", 0, ())
