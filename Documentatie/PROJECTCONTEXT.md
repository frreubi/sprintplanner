# Sprintplanner – projectcontext

**Inventarisdatum:** 5 november 2026  
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

## 3. Architectuurafspraken

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
