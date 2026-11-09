# Sprintplanner – projectcontext

**Versie:** 7 november 2026  
**Bijgewerkt op basis van:** inventaris 5 november en technische sessies 6–7 november 2026  
**Status:** actuele projectcontext; historische inventaris en eerdere proefresultaten zijn behouden.  

**Belangrijke leesregel:** de oorspronkelijke inventaris hieronder beschrijft de situatie op 5/6 november. De architectuurbesluiten en omgevingsgegevens in §12 zijn leidend waar ze afwijken van eerdere voorstellen of voorlopige aannames.

**Oorspronkelijke inventarisdatum:** 5 november 2026  
**Bron:** `Sprintplanner-inventaris-20261105-1458.zip`  
**Status:** eerste technische nulmeting; controleer wijzigingen na deze datum.

Dit document is het centrale vertrekpunt voor volgende werksessies. Het beschrijft de aangetroffen situatie en de gemaakte ontwerpafspraken. Bij tegenstrijdigheid tussen een oudere afspraak en de actuele broncode moet het verschil expliciet worden onderzocht; niet stilzwijgend aannemen welke juist is.

## 1. Werkwijze voor volgende sessies

Voor iedere technische wijziging:

1. Raadpleeg dit document.
2. Bepaal welke repository en welk bestand de wijziging betreft.
3. Controleer de actuele broncode en relevante imports voordat codeadvies wordt gegeven.
4. Geef één concrete wijziging tegelijk.
5. Vermeld expliciet welke gewijzigde bestanden naar de actieve LibreOffice-macromap moeten worden gekopieerd.
6. Houd repositorybestanden en actieve macrokopieën uit elkaar.
7. Werk dit document bij wanneer een architectuurafspraak, pad, interface of status verandert.

De gebruiker wil het Calc-document openen en verder niets handmatig starten. Geen terminalcommando, launcher of aparte configuratiestap mag onderdeel worden van de uiteindelijke gebruikersprocedure.

## 2. Lokale omgeving en paden

Gebruikersaccount op de ontwikkel-pc: `frreu`.

### 2.1 Repositories

| Onderdeel | Pad |
|---|---|
| Applicatie-repository | `C:\Users\frreu\Documents\LibreOfficeProject\Sprintplanner` |
| LibreOffice-integratie-repository | `C:\Users\frreu\Documents\LibreOfficeProject\LibreOffice` |

Dit zijn twee bewust gescheiden Git-repositories.

### 2.2 Actieve LibreOffice-macromap

`C:\Users\frreu\AppData\Roaming\LibreOffice\4\user\Scripts\python`

LibreOffice voert macro's uit vanuit deze map. Een wijziging in de repository `LibreOffice` wordt niet automatisch actief: gewijzigde macrobestanden moeten expliciet naar deze macromap worden gekopieerd.

### 2.3 Python-omgevingen

| Doel | Pad / versie |
|---|---|
| LibreOffice Python | `C:\Program Files\LibreOffice\program\python.exe` |
| Losse Python voor SprintInfo | `C:\Users\frreu\AppData\Local\Python\pythoncore-3.15-64\python.exe` |
| Eerder gebruikte LibreOffice Python | Python 3.13.15 (volgens projectnotities) |

`applicatie.py` gebruikt momenteel het expliciete Python 3.15-pad hierboven om `sprintinfo.py` als apart proces te starten.

### 2.4 Bestanden in LibreOffice-repository

- `sprintplanner.py` – beheerde macro-/adapterkopie.
- `verbinding.py` – klein bestand met UNO-testfunctie.
- `Verlof en Sprints 2026.ods` – Calc-werkboek.
- `Documentatie/API-contract_Sprintplanner.md` – API-contract.

### 2.5 Bestanden in Sprintplanner-repository

De inventaris bevat onder meer:

- `applicatie.py`
- `berekeningen.py`
- `sprintinfo.py`
- `medewerker.py`
- `rooster.py`
- `toewijzingen.py`
- `sprints.py`
- `kalender.py`
- `tests/`
- `logs/`
- `backups/`
- `verbinding.py`
- `connect.ps1`
- `start.py`
- `start_planner.py`
- `Verlof en Sprints 2026.ods` (kopie in deze repository)

De structuur-notitie in de repository zegt dat productiecode en bestanden die vaste paden verwachten voorlopig in de hoofdmap staan; er is bewust nog geen productiecode verplaatst.

## 3. Architectuurafspraken (oorspronkelijke afspraken; aangevuld en aangescherpt in §12)

De afgesproken verantwoordelijkheden zijn:

| Module | Verantwoordelijkheid |
|---|---|
| `sprintplanner.py` | LibreOffice-/Calc-adapter. Leest en schrijft Calc, zet Calc-gegevens om naar Python-objecten en vormt de macro-ingang. |
| `applicatie.py` | Centrale coördinatie. Ontvangt gegevens, roept berekeningen aan, maakt de gegevens voor SprintInfo gereed en start SprintInfo. Geen UNO- of Calc-afhankelijkheid. |
| `berekeningen.py` | Alle bedrijfs- en planningsberekeningen. Onafhankelijk van Calc en presentatie. |
| `sprintinfo.py` | Zelfstandig Tkinter-venster voor presentatie en gebruikersinteractie. |

Gegevensstroom bij starten:

`Calc → sprintplanner.py → applicatie.py → berekeningen.py → sprintinfo.py`

De applicatie mag niet afhankelijk worden van LibreOffice of UNO. De berekeningslaag blijft onafhankelijk van opslag en presentatie.

Het Calc-document is **leading**. De gebruiker opent `Verlof en Sprints 2026.ods`; de bestaande macrostart verzorgt de rest. De uiteindelijke gebruiker mag geen terminal, PowerShell-launcher of handmatige UNO-configuratie nodig hebben.

## 4. Aangetroffen start- en gegevensstroom

In de aangetroffen `sprintplanner.py` staat:

```python
def lees_planningsgegevens(*args):
    doc = XSCRIPTCONTEXT.getDocument()

    medewerkers = lees_medewerkers(doc)
    roosters = lees_roosters(doc)

    gegevens = {
        "sprints": lees_sprints(doc),
        "medewerkers": medewerkers,
        "roosters": roosters,
        "toewijzingen": lees_toewijzingen(doc, medewerkers, roosters),
        "afwezigheden": lees_afwezigheid(doc, medewerkers),
        "agile_instellingen": lees_agile_instellingen(doc),
        "uren_per_storypoint": lees_uren_per_storypoint(doc),
    }

    return gegevens


def start_applicatie(*args):
    gegevens = lees_planningsgegevens()
    applicatie.start(gegevens)
```

De complete gegevensset die nu wordt opgehaald bestaat uit:

- sprints;
- medewerkers;
- roosters;
- roostertoewijzingen;
- afwezigheden;
- agile-instellingen;
- uren per storypoint.

Ontwerpafspraak voor toekomstige verversing en Beheer: bij een nieuwe gegevensvraag wordt steeds de **volledige gegevensset** opnieuw uit Calc gelezen. De dataset is klein genoeg; deelgewijs ophalen is niet gewenst.

## 5. API-contract

Het API-contract staat als Markdown in beide repositories:

`Documentatie/API-contract_Sprintplanner.md`

De inventaris laat zien dat de twee Markdown-bestanden identiek zijn (SHA-256-prefix `33713de1cb193c91`).

De huidige startinterface is:

```python
applicatie.start(gegevens)
```

De gegevensdictionary heeft de sleutels `sprints`, `medewerkers`, `roosters`, `toewijzingen`, `afwezigheden`, `agile_instellingen` en `uren_per_storypoint`.

Het contract beschrijft ook de afzonderlijke JSON-overdracht van `applicatie.py` naar `sprintinfo.py`. Het contract is versie 1.0 van 3 november 2026 en noemt zelf nog openstaande specificaties, waaronder foutafhandeling, validatie, versie-identificatie en de volledige JSON-structuur.

**Let op:** de actuele berekeningscode heeft inmiddels ook `uren_per_werkstroom` toegevoegd. Controleer of het API-contract en de JSON-beschrijving dat veld volledig weerspiegelen voordat het contract als definitief wordt beschouwd.

## 6. Applicatielaag en SprintInfo – aangetroffen gedrag

### 6.1 `applicatie.py`

- `PROJECTMAP` wijst naar de Sprintplanner-repository.
- `PYTHON` wijst naar de afzonderlijke Python 3.15-installatie.
- `start(gegevens)` berekent per sprint de resultaten via `bereken_sprintresultaten(...)`.
- Sprintdatums worden vóór JSON-serialisatie omgezet naar ISO-datums.
- De resultaten worden geschreven naar `sprints.json`.
- Daarna wordt `sprintinfo.py` gestart als afzonderlijk proces.
- De omgeving verwijdert `PYTHONHOME` en `PYTHONPATH` voordat het proces start.

### 6.2 `sprintinfo.py`

De actuele inventarisversie bevat:
- zelfstandig Tkinter-venster;
- navigatie tussen vorige, huidige en volgende sprint;
- keuze tussen Storypoints en Uren;
- dynamische werkstroomkolommen;
- statusbeheer van navigatieknoppen.

De huidige sprintknop is bedoeld om uitgeschakeld te zijn wanneer de huidige sprint geselecteerd is, en actief te worden zodra de gebruiker naar een andere sprint navigeert. Bij terugkeer naar de huidige sprint wordt de knop weer uitgeschakeld.

Het venster blijft zelfstandig naast Calc bestaan. Dat gedrag moet behouden blijven.

### 6.3 Gewenste laatste functies

Nog te realiseren:
- refresh-pictogramknop (twee pijlen in een cirkel) rechtsboven;
- sluiten-pictogramknop rechtsboven;
- verversen haalt via de Calc-adapter een nieuwe volledige gegevensset op, herberekent en werkt de bestaande SprintInfo-weergave bij;
- na verversen blijft de gebruiker bij voorkeur op dezelfde geselecteerde sprint;
- sluiten beëindigt alleen SprintInfo en laat Calc/Sprintplanner verder ongemoeid;
- de latere Beheerfunctie gebruikt dezelfde route om de volledige gegevensset op te halen.

## 7. Twee repositories en synchronisatie

De twee repositories zijn bewust gescheiden:

1. `Sprintplanner`: applicatiecode, berekeningen, SprintInfo en tests.
2. `LibreOffice`: Calc-integratie, beheerde macro, werkboek en API-contract.

De actieve macrokopie staat daarnaast in de LibreOffice-gebruikersmap.

### Synchronisatieregel

Als `LibreOffice\sprintplanner.py` wijzigt, kopieer die dan naar:

`%APPDATA%\LibreOffice\4\user\Scripts\python\sprintplanner.py`

Als `LibreOffice\verbinding.py` wijzigt, kopieer die dan naar:

`%APPDATA%\LibreOffice\4\user\Scripts\python\verbinding.py`

Bij wijzigingen aan meerdere macro-afhankelijkheden moeten **alle gewijzigde bestanden** worden gekopieerd. Benoem de benodigde kopieercommando's expliciet bij de wijziging.

De applicatiebestanden uit de Sprintplanner-repository worden via de bestaande `sys.path`-verwijzing gevonden; ze worden niet zonder reden naar de macromap gekopieerd.

### Git-afspraken uit projectcontext

- Commit kleine, samenhangende wijzigingen.
- Houd de ODS-wijziging in de Sprintplanner-repository buiten commits tenzij daar expliciet anders over wordt besloten.
- Het `.docx`-API-contract is genegeerd via `*.docx`; Markdown is de bronversie.
- In de LibreOffice-repository is het initiële commitbericht `Initialiseer LibreOffice-integratie en Calc-werkboek`.
- In de Sprintplanner-repository was het meest recente commitbericht in de inventaris `Verbeter navigatie in SprintInfo`.

De ZIP bevat Git-metadata, maar is een momentopname en geen werkende checkout waarop betrouwbare actuele `git status`-resultaten moeten worden gebaseerd. Controleer Git-status altijd lokaal in de betreffende repository.

## 8. UNO en verbindingsbestanden – belangrijke bevinding

Dit is het belangrijkste punt uit de inventaris van 5 november 2026.

### 8.1 De drie relevante bestanden zijn niet hetzelfde

| Bestand | Inhoud / rol |
|---|---|
| `LibreOffice\verbinding.py` | 97 bytes; bevat `import uno` en `test_verbinding()`. |
| Actieve macromap `verbinding.py` | Exact dezelfde 97 bytes als de LibreOffice-repositorykopie. |
| `Sprintplanner\verbinding.py` | 1.145 bytes; bevat `verbind_met_calc()` en gebruikt `uno`, `subprocess` en `time`. |

De twee bestanden van 97 bytes zijn identiek (SHA-256-prefix `18b5076f263fea48`). De `Sprintplanner\verbinding.py` is een andere module met dezelfde modulenaam (SHA-256-prefix `70616e2982bbc5cd`).

### 8.2 Oorzaak van de fout op 5 november

De aangetroffen `LibreOffice\sprintplanner.py` en de actieve macrokopie zijn byte voor byte identiek (11.125 bytes; SHA-256-prefix `719f508356be5f7b`).

Bovenaan die macro staat:

```python
sys.path.append(
    r"C:\Users\frreu\Documents\LibreOfficeProject\Sprintplanner"
)
```

Daarna importeert hij onder meer:

```python
import verbinding
```

Omdat het pad naar de Sprintplanner-repository aan `sys.path` wordt toegevoegd, importeert Python de module `Sprintplanner\verbinding.py`. De log bevestigt dit expliciet:

`C:\Users\frreu\Documents\LibreOfficeProject\Sprintplanner\verbinding.py`

De geladen module bevat `verbind_met_calc`, niet `test_verbinding`. Daarom ontstond:

`AttributeError: module 'verbinding' has no attribute 'test_verbinding'`

Dit is dus geen vergeten argument en ook niet opgelost door alleen het kleine bestand naar de macromap te kopiëren: Python vindt een andere module met dezelfde naam via het eerder toegevoegde repositorypad.

**Niet op goed geluk imports of paden wijzigen.** Eerst bepalen welke UNO-verbindingsoplossing architectonisch de juiste wordt en daarna module-/naamconflicten expliciet oplossen.

### 8.3 Bestaande UNO-voorziening in de applicatierepository

`Sprintplanner\verbinding.py` bevat `verbind_met_calc()`:
- maakt een lokale UNO-context en URL-resolver;
- probeert verbinding te maken met `localhost`, poort `2002`;
- als dat mislukt, start het `soffice.exe` met `--accept` op `127.0.0.1:2002`;
- probeert daarna maximaal 20 keer opnieuw verbinding te maken;
- geeft een Desktop-object terug.

`Sprintplanner\connect.ps1` start LibreOffice eveneens met `--accept` op `127.0.0.1:2002`.

`Sprintplanner\start_planner.py` start LibreOffice met `--accept`, `--norestore`, `--nodefault` en het Calc-bestand als argument.

Deze bestaande scripts tonen aan dat er eerder een opstart-/verbindingstraject via `--accept` is gebruikt. Ze bewijzen **niet** dat de huidige macrogestuurde documentstart zelf een UNO-listener activeert.

### 8.4 Harde ontwerpvoorwaarden voor de nieuwe verbinding

- Calc-document blijft leading.
- De gebruiker opent uitsluitend `Verlof en Sprints 2026.ods`.
- Geen handmatige terminal, PowerShell of aparte launcher voor eindgebruikers.
- Geen afhankelijkheid van onbeheerde LibreOffice-configuratie die binnen een organisatie afgeschermd kan zijn.
- Indien een externe UNO-verbinding nodig is, uitsluitend lokaal (`localhost`/loopback) toegankelijk.
- Geen onbewezen claim dat een macro automatisch een blijvende UNO-server/acceptor activeert.
- Eerst een kleine technische proef; pas na aantoonbaar succes integreren.
- `applicatie.py` en `berekeningen.py` mogen geen UNO-afhankelijkheid krijgen.
- Dezelfde gegevensroute moet later bruikbaar zijn voor verversen én Beheer.

## 9. Huidige ontwikkelstatus op basis van de inventaris

### Gereed / aanwezig
- Twee gescheiden Git-repositories.
- Calc-werkboek en macro-integratie.
- Centrale `lees_planningsgegevens()`-functie.
- Berekening van sprintresultaten.
- Zelfstandig SprintInfo-venster.
- Navigatie tussen sprints.
- Weergaveschakelaar Storypoints/Uren.
- Testsuite in de Sprintplanner-repository.
- API-contract als Markdown in beide repositories.

Volgens de meest recente projectnotitie vóór deze inventarisatie waren 60 unittests geslaagd. Dit is een eerder gerapporteerd resultaat, geen test die tijdens het maken van dit document opnieuw is uitgevoerd.

### Eerstvolgende werkzaamheden
1. UNO-communicatie vanuit de reeds geopende Calc-sessie technisch bewijzen, zonder gebruikershandeling.
2. De naam-/importbotsing rond `verbinding.py` oplossen op basis van een bewuste ontwerpkeuze.
3. Een veilige lokale communicatie-interface maken waarmee SprintInfo de macro/adapter om een volledige nieuwe dataset kan vragen.
4. Applicatie herberekenen en bestaande SprintInfo-weergave verversen.
5. Refresh- en sluiten-pictogramknoppen toevoegen.
6. Dezelfde gegevensvoorziening voorbereiden voor Beheer.
7. API-contract in beide repositories bijwerken wanneer de interface is uitgewerkt.

## 10. Inventarisbeperkingen

Deze nulmeting is gebaseerd op de inhoud van de aangeleverde ZIP van 5 november 2026. De ZIP bevat de twee repositories en de actieve macromap zoals door het PowerShell-commando verzameld. Hij is geen volledige kopie van de C-schijf.

Niet vastgesteld door deze inventaris:
- de actuele toestand op de pc ná het maken van de ZIP;
- de huidige Git-status na het uploadmoment;
- welke LibreOffice-processen of UNO-listeners op dit moment actief zijn;
- of de macro vanuit een al geopende Calc-sessie zelf een acceptor kan starten die bruikbaar blijft;
- of de huidige lokale Python-installaties en paden inmiddels zijn gewijzigd.

Controleer deze zaken op de pc wanneer ze relevant worden. Vraag de gebruiker niet om bekende gegevens opnieuw te zoeken als ze uit de aangeleverde bestanden kunnen worden afgeleid.

## 11. Voortgang UNO-bridge-proef – 6 november 2026

Deze sectie is toegevoegd na de technische sessie van 6 november. De oorspronkelijke inventaris hierboven blijft behouden; de bevindingen hieronder zijn gebaseerd op de uitgevoerde praktijktests en de getoonde code/logs.

### 11.1 Module- en padwijziging

- De kleine LibreOffice-module is hernoemd van `verbinding.py` naar `lo_verbinding.py` om de naamconflict met `Sprintplanner\\verbinding.py` te vermijden.
- `sprintplanner.py` importeert nu `lo_verbinding`.
- In `sprintplanner.py` is het actieve macropad vooraan aan `sys.path` toegevoegd met `sys.path.insert(0, r"C:\\Users\\frreu\\AppData\\Roaming\\LibreOffice\\4\\user\\Scripts\\python")`.
- De gebruiker heeft vanuit Calc bevestigd dat de macro zonder importfout opent en `test_uno_verbinding` werkt.
- Bij de bridgeproef wordt `start_acceptor_test` vanuit de macro aangeroepen met `XSCRIPTCONTEXT.getDocument()` als argument. De functie in `lo_verbinding.py` moet daarom `def start_acceptor_test(document):` accepteren. Tijdens de sessie is eerst een mismatch met een nulargumentige versie vastgesteld; daarna is de documentparameter in de servercode gebruikt.

### 11.2 Huidige testopstelling

De UNO-bridge wordt experimenteel vanuit de bestaande Calc-sessie gestart door een macro. De servercode gebruikt:
- `com.sun.star.connection.Acceptor`;
- een luisterthread die `accept("socket,host=127.0.0.1,port=2002")` uitvoert;
- een `InstanceProvider` die `com.sun.star.bridge.XInstanceProvider` implementeert;
- `BridgeFactory.createBridge("SprintplannerBridge", "urp", verbinding, provider)`;
- de instantie-naam `document` om het Calc-document aan de client beschikbaar te stellen.

De provider heeft deze vorm:

```python
class InstanceProvider(unohelper.Base, XInstanceProvider):
    def __init__(self, document):
        self.document = document

    def getInstance(self, naam):
        if naam == "document":
            return self.document
        raise Exception(f"Onbekend object: {naam}")
```

De serverlog staat op:

`C:\\Users\\frreu\\Documents\\LibreOfficeProject\\Sprintplanner\\logs\\acceptor_test.log`

De serverlog toonde onder meer:

```text
Bridge-test gestart
Wachten op client
Client verbonden
UNO-bridge aangemaakt
getInstance aangeroepen: document
Document beschikbaar: True
Document wordt teruggegeven
```

Dit bevestigt dat de acceptor een clientverbinding accepteert, de serverbridge wordt aangemaakt en de provider wordt aangeroepen met een beschikbaar documentobject.

### 11.3 Bewezen clienttest

De clienttest wordt uitgevoerd met de LibreOffice-interpreter, niet met de losse Python 3.15-interpreter:

```powershell
& "C:\\Program Files\\LibreOffice\\program\\python.exe" -u .\\test_bridge.py
```

`import uno` werkt in deze interpreter (`UNO beschikbaar`). In de losse Python 3.15-installatie ontbreekt `uno` (`ModuleNotFoundError`). De Python 3.15-interpreter blijft de beoogde interpreter voor SprintInfo; de UNO-clientproef draait vooralsnog met LibreOffice Python.

Een volledige test op het werkblad `Medewerkers` is geslaagd. De client kon achtereenvolgens:
- verbinding maken;
- de bridge aanmaken;
- `bridge.getInstance("document")` uitvoeren;
- werkblad `Medewerkers` ophalen;
- bereik `A1:D5` met `getDataArray()` uitlezen;
- daarna nog een afzonderlijke cel `A1` met `getString()` uitlezen;
- de verbinding aan het einde sluiten.

Uitvoer:

```text
1. Python gestart
2. Connector aangemaakt
3. Verbinding gemaakt
4. Bridge aangemaakt
5. Document opgehaald
Rij 1: ('Userid ', 'Voornaam ', 'Tussenvoegsel ', 'Achternaam ')
Rij 2: ('j001', 'Jan', 'van der', 'Berg')
Rij 3: ('p002', 'Petra', '', 'Jansen')
Rij 4: ('a003', 'Ahmed', '', 'Bakker')
Rij 5: ('frreu', 'Roel', '', 'Rigterink')
6. Werkblad opgehaald
7. Celobject opgehaald
8. Celwaarde: 'Userid '
9. Verbinding gesloten
```

**Belangrijke correctie op eerdere diagnose:** `getDataArray()` is niet de oorzaak van het eerdere vastlopen. In de mislukte clienttest stond `verbinding.close()` direct na de `getDataArray()`-lus, waarna nog een cel via dezelfde bridge werd opgevraagd. De daaropvolgende `DisposedException` werd veroorzaakt doordat de transportverbinding al gesloten was. Na verplaatsing van `verbinding.close()` naar het einde slaagde de volledige test.

### 11.4 Huidige status en nog niet bewezen

**Bewezen:** een clientproces met LibreOffice Python kan via de experimentele acceptor/bridge het bestaande Calc-document benaderen en meerdere UNO-aanroepen achter elkaar uitvoeren, inclusief `getDataArray()` en `getString()`, zolang de verbinding niet voortijdig wordt gesloten.

**Nog niet bewezen / nog te onderzoeken:**
- of de acceptor/luisterthread op een nette en betrouwbare manier meerdere opeenvolgende clientaanvragen kan accepteren;
- of per aanvraag een nieuwe bridge/verbinding moet worden gemaakt, of dat een andere serveropzet beter is;
- hoe de bridge en luisterthread worden beëindigd wanneer Calc wordt gesloten;
- hoe de externe Python 3.15-applicatie de gegevens veilig kan opvragen zonder zelf `uno` nodig te hebben;
- hoe de volledige dataset van zeven werkbladen wordt overgedragen, bij voorkeur als JSON;
- hoe de acceptor automatisch onderdeel wordt van de normale Calc-start, zonder handmatige handeling voor de eindgebruiker.

Een `NoConnectException (WSAECONNREFUSED)` trad op nadat het Calc-bestand opnieuw was geopend maar de acceptor niet expliciet was gestart. Het openen van het ODS-bestand alleen startte de experimentele acceptor dus niet automatisch.

Een `DisposedException` trad ook op toen Calc tijdens een lopende clienttest werd afgesloten. Dat is te verwachten wanneer UNO-objecten worden gebruikt nadat de Calc-sessie/bridge is beëindigd; de client moet dit als sessie-einde kunnen afhandelen.

Het bewaren van de geaccepteerde verbinding in een globale variabele `_verbinding` is als experiment toegevoegd. Dit heeft op zichzelf de eerdere fout niet opgelost; de doorslaggevende fout in de geslaagde test was de te vroeg uitgevoerde `verbinding.close()` in de client.

### 11.5 Startpunt volgende werksessie

1. Begin met de bewezen werkende `test_bridge.py`-variant waarin `verbinding.close()` uitsluitend aan het einde staat.
2. Verifieer de actuele `lo_verbinding.py`, `sprintplanner.py` en actieve macrokopie; ga niet uit van bestanden die alleen in de repository zijn opgeslagen.
3. Ontwerp daarna gecontroleerd een herhaalbare serverlus: acceptor blijft luisteren zolang Calc open is; per clientaanvraag wordt de verbinding/bridge correct beheerd en afgesloten; daarna wacht de server op de volgende aanvraag. Test eerst twee opeenvolgende aanvragen met een kleine dataset.
4. Onderzoek expliciet hoe een macrogestarte luisterthread zich gedraagt bij afsluiten van Calc en hoe die lifecycle veilig wordt beheerd.
5. Pas als herhaalde aanvragen betrouwbaar werken, bouw de volledige datasetoverdracht naar JSON en de koppeling met Python 3.15/SprintInfo.

Laat de gebruiker voorlopig de acceptor handmatig vanuit Calc starten voor de proef. Dit is uitsluitend een ontwikkeltest en nadrukkelijk niet de uiteindelijke gebruikersprocedure.

**Laatste bewezen status per 6 november 2026:** één volledige UNO-clienttransactie is succesvol en snel uitgevoerd; herhaalde transacties en automatische acceptorstart zijn nog openstaand.


## 12. Architectuurbesluit: interpreter-onafhankelijke applicatiegrens – 7 november 2026

### 12.1 Aanleiding en bevestiging van het oorspronkelijke uitgangspunt

De privé-pc en de werklaptop gebruiken verschillende LibreOffice-versies en verschillende Python-versies die met LibreOffice worden meegeleverd. Dit bevestigt dat de applicatie niet afhankelijk mag zijn van de Python-runtime van LibreOffice.

De gebruiker bevestigt dat deze scheiding vanaf het begin het uitgangspunt was, mede met het oog op een mogelijke Excel-variant. De architectuur moet daarom meerdere gegevensbronnen/adapters kunnen ondersteunen zonder de applicatie- of berekeningslogica te wijzigen.

### 12.2 Definitieve ontwerpafspraken

1. **LibreOffice-adapter** (`sprintplanner.py` en UNO-gerelateerde integratie) is uitsluitend verantwoordelijk voor communicatie met Calc, het lezen en schrijven van Calc-gegevens en de vertaling naar/van het afgesproken gegevenscontract.
2. **Applicatie** (`applicatie.py`) is zelfstandig en bevat geen afhankelijkheid van LibreOffice, Calc of UNO.
3. **Berekeningen** (`berekeningen.py`) bevatten uitsluitend bedrijfs- en planningslogica. Geen afhankelijkheid van Calc, UNO, JSON, bestanden of presentatie.
4. **Presentatie** (`sprintinfo.py`) blijft een zelfstandige gebruikersinterface. De bestaande JSON-overdracht van applicatie naar SprintInfo is een afzonderlijke interface en staat los van de adaptergrens.
5. **Adapter ↔ applicatie:** gegevens worden uitgewisseld via een expliciet, interpreter-onafhankelijk en versieerbaar contract. JSON is hiervoor het voorkeursformaat. Er worden geen Python-objecten, klassereferenties of UNO-objecten over deze grens gedeeld.
6. **Excel-uitbreiding:** een toekomstige Excel-adapter moet hetzelfde contract kunnen gebruiken. De applicatie en berekeningen worden daarvoor niet aangepast.
7. De LibreOffice-adapter mag de Python-versie gebruiken die bij de lokaal geïnstalleerde LibreOffice hoort. De zelfstandige applicatie mag een eigen ondersteunde Python-versie gebruiken.
8. De organisatieomgeving/werklaptop is een bepalende compatibiliteitsomgeving. Een oplossing is pas portabel als de relevante tests op beide omgevingen slagen.
9. De eindgebruiker opent uiteindelijk alleen het Calc-werkboek; er mag geen handmatige terminal-, PowerShell- of UNO-configuratiestap nodig zijn.

### 12.3 Beoogde gegevensstroom

```text
LibreOffice Calc
      ↕
LibreOffice-adapter (Python/PyUNO van LibreOffice)
      ↕
Versieerbaar gegevenscontract (voorkeur: JSON)
      ↕
Zelfstandige applicatie (eigen Python-runtime)
      ├── berekeningen.py
      └── sprintinfo.py
```

Een toekomstige Excel-adapter sluit op dezelfde contractgrens aan:

```text
Excel ↔ Excel-adapter ↔ hetzelfde gegevenscontract ↔ applicatie
```

De precieze transportvoorziening tussen adapter en applicatie is nog niet definitief gekozen. Mogelijke transportvormen moeten worden beoordeeld op organisatiebeleid, lokale beveiliging, rechten, betrouwbaarheid en eenvoudige installatie. JSON beschrijft de gegevensstructuur; het schrijft op zichzelf nog geen transportprotocol voor.

### 12.4 Wat dit betekent voor de huidige code

De huidige implementatie roept vanuit de Calc-macro rechtstreeks `applicatie.start(gegevens)` aan en geeft daarbij Python-objecten door. Dit is de bestaande situatie, niet de gewenste definitieve adaptergrens.

De huidige `applicatie.py` wordt op dit moment geïmporteerd en uitgevoerd binnen het LibreOffice-Pythonproces. Het expliciete Python 3.15-pad in `applicatie.py` wordt gebruikt om `sprintinfo.py` als apart proces te starten; het betekent niet dat `applicatie.py` zelf momenteel onder Python 3.15 draait.

Deze implementatie moet stapsgewijs worden aangepast. Niet vooruitlopend op het transport alvast een JSON-serialisatiemodule bouwen zonder eerst het contract en de transportkeuze vast te leggen.

De UNO-acceptor/bridge-proef uit §11 blijft bruikbaar als technische verkenning van toegang tot Calc. De bewezen UNO-verbinding is echter niet de architectuurgrens tussen adapter en applicatie. De applicatie zelf krijgt geen UNO-afhankelijkheid.

### 12.5 Omgevingen vastgesteld op 7 november 2026

| Onderdeel | Privé-pc | Werklaptop |
|---|---|---|
| LibreOffice | 26.8.1.1 (x86_64) | 26.2.6.3 (x86_64) |
| Windows | Windows 11, build 26300 | Windows 11, build 26200 |
| LibreOffice-Python | 3.13.15 | 3.12.14 |
| Python-DLL | `python313.dll` | `python312.dll` |
| `pyuno.pyd` | aanwezig | aanwezig |
| `import uno, unohelper, pyuno` via LibreOffice-Python | geslaagd | geslaagd |

Zelfstandige Python op privé-pc:

| Interpreter | Tkinter | UNO |
|---|---|---|
| Python 3.15.2 | ontbreekt | `uno` ontbreekt |
| Python 3.13 (pythoncore-3.13-64) | werkt | werkt na toevoegen van LibreOffice-programmapad en DLL-zoekpad |

De succesvolle test voor zelfstandige Python 3.13 was:

```powershell
py -3.13 -c "import os,sys; p=r'C:\Program Files\LibreOffice\program'; os.add_dll_directory(p); os.environ['PATH']=p+';'+os.environ['PATH']; sys.path.insert(0,p); import uno,unohelper; print('UNO OK'); print(uno.__file__)"
```

Uitvoer: `UNO OK`, met `uno.py` geladen vanuit de LibreOffice-programmamap.

**Interpretatie:** deze test toont dat UNO technisch vanuit de zelfstandige Python 3.13 op de privé-pc kan worden geladen. Dit is nadrukkelijk geen reden om de zelfstandige applicatie afhankelijk te maken van PyUNO. De werklaptop gebruikt Python 3.12 voor LibreOffice; de `pyuno.pyd` daarvan is niet uitwisselbaar met de Python 3.13-runtime. De test onderstreept juist waarom de adaptergrens interpreter-onafhankelijk moet zijn.

### 12.6 Compatibiliteits- en beheerbeleid

Bij verdere ontwikkeling gelden de volgende regels:

- Geen afhankelijkheid van de exacte Python-versie die LibreOffice meelevert buiten de adapter.
- Geen kopiëren van `pyuno.pyd`, Python-DLL's of andere LibreOffice-runtimebestanden tussen computers.
- Geen aanname dat de organisatie Python, LibreOffice, DLL's of pakketten vrij laat installeren of bijwerken.
- De organisatieomgeving bepaalt mede welke installatie- en communicatievorm acceptabel is.
- Onderzoek vóór implementatie of lokale socket-/poortcommunicatie, subprocessen en benodigde bestanden door het organisatiebeleid zijn toegestaan.
- Test de adapter met de Python/PyUNO-combinatie van de betreffende LibreOffice-installatie.
- Test de zelfstandige applicatie met de gekozen eigen Python-runtime, onafhankelijk van PyUNO.
- Leg ondersteunde versies en afhankelijkheden vast zodra de organisatieomgeving volledig is geïnventariseerd.
- De uiteindelijke gebruikersprocedure mag geen handmatige configuratie van UNO-acceptors of poorten vragen.

### 12.7 API-contract bijwerken

Het bestaande `Documentatie/API-contract_Sprintplanner.md` is versie 1.0 van 3 november 2026. Het beschrijft al de scheiding tussen adapter, applicatie en berekeningen en de onafhankelijkheid van de gegevensbron, maar de feitelijke startinterface geeft nog Python-objecten rechtstreeks door.

De volgende contractversie moet daarom expliciet vastleggen:

- contractnaam en versienummer;
- bericht-/gegevensstructuur voor de volledige dataset;
- datumnotatie en representatie van lege waarden;
- identificatie en verwijzingen tussen medewerkers, roosters en toewijzingen;
- verplichte en optionele velden en validatieregels;
- foutmeldingen en foutafhandeling;
- compatibiliteitsregels bij een contractwijziging;
- transportonafhankelijkheid: JSON is de payload, transport wordt apart gekozen;
- gebruik door zowel LibreOffice- als een toekomstige Excel-adapter.

De bestaande dataset bevat momenteel de sleutels `sprints`, `medewerkers`, `roosters`, `toewijzingen`, `afwezigheden`, `agile_instellingen` en `uren_per_storypoint`. Controleer bij het actualiseren van het contract ook de inmiddels toegevoegde instelling `uren_per_werkstroom` en de actuele berekeningscode. Ga niet uit van een oudere lijst zonder broncodecontrole.

Het contractbestand in beide repositories moet identiek worden bijgewerkt:

- `Sprintplanner\Documentatie\API-contract_Sprintplanner.md`
- `LibreOffice\Documentatie\API-contract_Sprintplanner.md`

### 12.8 Startpunt volgende werksessie

1. Gebruik dit projectcontextdocument als vertrekpunt; §12 is leidend voor de architectuur.
2. Controleer eerst de actuele bestanden en Git-status in de privé-repositories. Houd de werklaptop/repository strikt gescheiden; er hoeft nu niets naar de werklaptop te worden gekopieerd.
3. Werk het API-contract bij naar een nieuwe versie die de expliciete interpreter-onafhankelijke adaptergrens beschrijft. Controleer daarvoor de actuele domeinklassen en berekeningscode, inclusief `uren_per_werkstroom`.
4. Ontwerp daarna de payload en validatie met representatieve gegevens; leg nog geen transport vast voordat de organisatiebeperkingen zijn onderzocht.
5. Vergelijk transportopties (bijvoorbeeld lokale bestandsoverdracht of loopback-communicatie) op beheerbaarheid, beveiliging, foutafhandeling en gebruikersgemak.
6. Bouw een kleine adaptercontracttest waarmee dezelfde dataset vanuit verschillende adapters kan worden aangeleverd en door dezelfde applicatie kan worden verwerkt.
7. Behoud de bestaande UNO-bridge als afzonderlijke technische proef; integreer die pas wanneer duidelijk is welke rol hij in de gekozen adapter/transportopzet krijgt.

**Laatste architectuurbesluit per 7 november 2026:** applicatie en berekeningen zijn onafhankelijk van LibreOffice, UNO en de LibreOffice-Python-runtime. Adaptergegevens gaan over een expliciet, versieerbaar, interpreter-onafhankelijk contract (voorkeur JSON). Een toekomstige Excel-adapter gebruikt hetzelfde contract. De transportkeuze is nog open en moet mede passen binnen het beheer- en beveiligingsbeleid van de organisatie.
