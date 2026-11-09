# API-contract Sprintplanner

**Versie:** 2.0 (herzien concept ter review)  
**Status:** ontwerp; nog niet geïmplementeerd  
**Doel:** interpreter-onafhankelijke gegevensuitwisseling tussen een gegevensbronadapter en de Sprintplanner-applicatie.

## 1. Doel en uitgangspunten

Dit contract beschrijft de gegevens die een adapter aan de zelfstandige Sprintplanner-applicatie overdraagt. De adapter kan bijvoorbeeld LibreOffice Calc of in de toekomst Excel zijn.

De afspraken zijn:

- De adapter leest en schrijft de gegevensbron en vertaalt die naar dit contract.
- De applicatie en berekeningen zijn niet afhankelijk van Calc, UNO, Excel, JSON-bestanden of de Python-runtime van de adapter.
- Over de adapter-/applicatiegrens worden uitsluitend contractgegevens overgedragen: geen Python-objecten, klassereferenties of UNO-objecten.
- Binnen de applicatie blijft het objectgeoriënteerde domeinmodel behouden. De applicatie zet de ontvangen contractgegevens om naar domeinobjecten; bedrijfslogica en berekeningen werken met die objecten.
- Dit contract schrijft geen intern dictionary-model voor. JSON-objecten zijn uitsluitend de externe representatie van de gegevens.
- JSON is het afgesproken payloadformaat. Het transport (bestand, lokale communicatie of een andere voorziening) wordt afzonderlijk gekozen.
- Een toekomstige Excel-adapter gebruikt hetzelfde contract.
- De bestaande overdracht van de applicatie naar SprintInfo is een afzonderlijke interface en valt niet samen met dit invoercontract.

## 2. Architectuur en gegevensstromen

```text
LibreOffice Calc ── LibreOffice-adapter ──┐
                                         ├── Contract 2.0 (JSON) ── Applicatie ── Berekeningen
Excel ───────────── Excel-adapter ────────┘                                  │
                                                                             └── SprintInfo-contract (apart)
```

De adapter is verantwoordelijk voor brongebonden conversies. De applicatie valideert het ontvangen contract, vertaalt de gegevens naar domeinobjecten en coördineert de verwerking. De berekeningslaag bevat bedrijfs- en planningslogica en werkt met de domeinobjecten, niet rechtstreeks met JSON.

## 3. Intern domeinmodel en vertaling

Het JSON-contract bepaalt uitsluitend de gegevensuitwisseling tussen adapter en applicatie. Het bepaalt niet hoe de applicatie haar interne code organiseert.

De bestaande objectgeoriënteerde aanpak blijft behouden. Eigenschappen en gedrag die bij een domeinbegrip horen, blijven waar mogelijk bij elkaar in de bijbehorende klasse. De applicatie maakt na ontvangst van de payload domeinobjecten aan en geeft die door aan de bedrijfslogica.

De beoogde vertaling is:

| Contractonderdeel | Intern domeinmodel |
|---|---|
| `medewerkers` | `Medewerker`-objecten |
| `roosters` | `Rooster`-objecten |
| `toewijzingen` | `Roostertoewijzing`-objecten, gekoppeld aan medewerker en rooster |
| `sprints` | `Sprint`-objecten |
| `afwezigheden` | Afwezigheidsgegevens in de vorm die het domeinmodel/berekeningen nodig hebben; een aparte klasse is niet verplicht |
| `agile_instellingen` | De bestaande interne representatie voor agile-instellingen |
| `instellingen` | Applicatie-instellingen, waaronder uren per storypoint en werkstromen |

De namen in de rechterkolom verwijzen naar de bestaande domeinklassen of interne representaties. Bij implementatie worden de actuele constructors en interfaces gecontroleerd; dit contract schrijft geen nieuwe klassesignatures voor.

**Belangrijke scheiding:**

1. De adapter leest de bron en produceert gegevens volgens dit contract.
2. De applicatie valideert de payload en bouwt daaruit domeinobjecten op.
3. De berekeningen ontvangen en gebruiken domeinobjecten.
4. Bij uitvoer naar een andere component wordt opnieuw een expliciete gegevensrepresentatie gemaakt.

Identificaties zoals `userid` en `rooster_id` worden gebruikt om relaties over de JSON-grens uit te drukken. Na het inlezen mag de applicatie deze identificaties gebruiken om de passende objectrelaties op te bouwen. De interne code hoeft dus niet overal met losse ID's te blijven werken als een objectrelatie passender is.

JSON-serialisatie en -deserialisatie horen bij de grens-/vertaallaag. Domeinklassen hoeven niet afhankelijk te worden van JSON, Calc, UNO of een specifieke adapter.

## 4. Envelope en top-level structuur

Een bericht heeft de volgende structuur:

```json
{
  "contract": {
    "naam": "Sprintplanner",
    "versie": "2.0"
  },
  "sprints": [],
  "medewerkers": [],
  "roosters": [],
  "toewijzingen": [],
  "afwezigheden": [],
  "agile_instellingen": [],
  "instellingen": {
    "uren_per_storypoint": 6.0,
    "werkstromen": ["ops", "dev", "func", "access"]
  }
}
```

Alle top-level onderdelen zijn verplicht. Een lege lijst is toegestaan als het betreffende onderdeel geen records bevat. `instellingen.uren_per_storypoint` moet een positief getal zijn. `instellingen.werkstromen` is de geordende lijst van werkstroomnamen die de adapter uit de bron leest; deze lijst wordt expliciet opgenomen zodat de applicatie niet afhankelijk is van Calc-cellen.

**Migratie-opmerking:** de huidige adapter geeft `uren_per_storypoint` afzonderlijk door en gebruikt de werkstroomlijst uit `Instellingen!B6` om medewerkers te lezen. De huidige `lees_planningsgegevens()` geeft die werkstroomlijst zelf niet door. Het gegroepeerde `instellingen`-object is dus een contractwijziging die bij implementatie in adapter én applicatie moet worden doorgevoerd.

## 5. Algemene representatieregels

- JSON-teksten zijn UTF-8.
- Datums zijn strings in ISO 8601-kalendernotatie `YYYY-MM-DD`.
- Een ontbrekende optionele datum wordt weergegeven als `null`, niet als lege string.
- Booleans zijn JSON `true` of `false`.
- Getallen zijn JSON-nummers, geen numerieke strings.
- Identificaties (`userid`, `rooster_id`) zijn strings en worden als verwijzingen gebruikt.
- JSON-objectsleutels zijn strings. Datumwaarden worden daarom niet als objectkey gebruikt.
- De adapter normaliseert werkstroomnamen naar kleine letters, overeenkomstig de huidige verwerking.

## 6. Gegevensonderdelen

### 5.1 Sprints

`sprints` is een lijst met:

```json
{
  "naam": "Sprint 2026-Week 45",
  "begindatum": "2026-11-02",
  "einddatum": "2026-11-13"
}
```

Velden:

- `naam`: tekst, verplicht.
- `begindatum`: ISO-datum, verplicht.
- `einddatum`: ISO-datum, verplicht; inclusief deze dag.

De begin- en einddatum vormen samen de periode waarop de sprintberekening wordt uitgevoerd. `einddatum` mag niet vóór `begindatum` liggen.

### 5.2 Medewerkers

`medewerkers` is een lijst met:

```json
{
  "userid": "j001",
  "voornaam": "Jan",
  "tussenvoegsel": "van der",
  "achternaam": "Berg",
  "rol": "dev",
  "werkstromen": {
    "dev": 70,
    "ops": 20,
    "func": 10,
    "access": 0
  },
  "beheerder": false,
  "access_analist": false,
  "einddatum": null
}
```

Velden:

- `userid`: niet-lege, unieke tekst; primaire identificatie.
- `voornaam`: niet-lege tekst.
- `tussenvoegsel`: tekst; lege tekst is toegestaan.
- `achternaam`: niet-lege tekst.
- `rol`: niet-lege tekst; huidige domeinklasse normaliseert deze naar kleine letters.
- `werkstromen`: object met werkstroomnaam als sleutel en percentage als waarde.
- `beheerder`: boolean.
- `access_analist`: boolean.
- `einddatum`: ISO-datum of `null`.

Percentages zijn getallen van 0 tot en met 100. De som van de percentages hoort 100 te zijn. In de huidige code levert een afwijkende som een waarschuwing op; het is geen harde validatiefout. Deze bestaande gedragskeuze blijft in dit contract een waarschuwing, tenzij later anders besloten.

**Actieve periode:** de medewerker telt mee tot en met `einddatum`. Vanaf de dag na de einddatum wordt de medewerker niet meegenomen in berekeningen. `null` betekent dat geen einddatum is ingesteld. Dit is een vastgesteld ontwerpbesluit, maar is nog niet in de huidige berekeningscode geïmplementeerd.

### 5.3 Roosters

`roosters` is een lijst met:

```json
{
  "rooster_id": "R02",
  "cyclus_weken": 2,
  "uren_per_week": [
    [8, 8, 8, 8, 4],
    [8, 8, 4, 8, 0]
  ]
}
```

Velden:

- `rooster_id`: niet-lege, unieke tekst.
- `cyclus_weken`: integer `1` of `2`.
- `uren_per_week`: lijst met exact `cyclus_weken` weekpatronen.
- Elk weekpatroon bevat exact vijf getallen, in volgorde maandag tot en met vrijdag.
- Per werkdag is `0` tot en met `9` uur toegestaan. `0` betekent geen roosteruren op die dag.

Een eenweeksrooster heeft vijf dagwaarden; een tweeweeksrooster heeft tien dagwaarden, verdeeld over twee afzonderlijke weekpatronen. De patronen van week 1 en week 2 mogen van elkaar verschillen.

**Cyclusbepaling:** de bestaande logica gebruikt het ISO-weeknummer. Bij een cyclus van één week wordt steeds patroon 1 gebruikt. Bij een cyclus van twee weken wordt patroon 1 gebruikt voor oneven ISO-weeknummers en patroon 2 voor even ISO-weeknummers. Er wordt geen individuele startdatum voor de cyclus meegestuurd.

**Migratie-opmerking:** de huidige klasse `Rooster` accepteert nog 0 tot en met 24 uur per dag. De contractregel 0 tot en met 9 uur is een nieuwe functionele grens en vereist later een wijziging van de domeinvalidatie.

### 5.4 Roostertoewijzingen

`toewijzingen` is een lijst met:

```json
{
  "userid": "j001",
  "rooster_id": "R02",
  "geldig_vanaf": "2026-01-01",
  "geldig_tm": null
}
```

Velden:

- `userid`: verwijst naar precies één medewerker.
- `rooster_id`: verwijst naar precies één rooster.
- `geldig_vanaf`: ISO-datum, verplicht.
- `geldig_tm`: ISO-datum of `null`; indien gevuld is deze datum inbegrepen.

De geldigheidsperiode is inclusief begin- en einddatum. `geldig_tm` mag niet vóór `geldig_vanaf` liggen. Voor dezelfde medewerker mogen geldigheidsperioden niet overlappen. Een medewerker kan opeenvolgende toewijzingen hebben.

Een medewerker die binnen de berekeningsperiode actief is, moet voor iedere actieve dag precies één geldige roostertoewijzing hebben. Een ontbrekende toewijzing is een harde contract-/gegevensfout en mag niet worden behandeld als nul roosteruren of stilzwijgend worden overgeslagen. De geldigheidsperioden van de toewijzingen moeten samen dus de volledige actieve periode binnen de berekeningsperiode afdekken. De applicatie meldt de medewerker en de datum waarop de dekking ontbreekt.

De huidige functies verschillen hierin nog: `zoek_toewijzing()` en `bereken_roosteruren()` geven een fout, terwijl `bereken_netto_uren_medewerkers()` een medewerker zonder geldige toewijzing op een dag overslaat. Die afwijking moet bij implementatie worden opgeheven.

### 5.5 Afwezigheden

`afwezigheden` is één centrale lijst:

```json
[
  {
    "userid": "j001",
    "datum": "2026-11-03",
    "code": "V"
  },
  {
    "userid": "j001",
    "datum": "2026-11-04",
    "code": "4V"
  }
]
```

Velden:

- `userid`: verwijst naar een bestaande medewerker.
- `datum`: ISO-datum.
- `code`: niet-lege tekst.

De combinatie `userid` + `datum` mag maximaal eenmaal voorkomen. De adapter vertaalt de huidige Calc-indeling (medewerker per rij, datums horizontaal) naar deze lijst en gebruikt `userid` als sleutel; koppeling op volledige naam wordt niet gebruikt in het nieuwe contract.

De huidige berekeningsfunctie herkent de codes `V`, `B`, `C` en `Z` als volledige afwezigheid van de roosteruren. Codes die eindigen op een van deze letters en voorafgegaan worden door een getal, zoals `4V`, leveren het opgegeven aantal afwezigheidsuren op. Andere codes veroorzaken een fout. De toegestane codes en aanvullende bereikcontroles moeten bij de implementatie expliciet worden gevalideerd.

### 5.6 Agile-instellingen

`agile_instellingen` is een lijst met:

```json
{
  "type": "DagStart",
  "dagen": ["ma", "di", "do"],
  "duur": 0.5
}
```

Velden:

- `type`: tekst.
- `dagen`: lijst met dagafkortingen.
- `duur`: getal.

De toegestane waarden voor `type` zijn `DagStart`, `Refinement` en `Sprintwissel`. `dagen` bevat uitsluitend de afkortingen `ma`, `di`, `wo`, `do` en `vr`. `duur` is een positief getal. `Sprintwissel` wordt gekoppeld aan de eerste dag van de sprint in de berekening.

### 5.7 Algemene instellingen

`instellingen` bevat:

```json
{
  "uren_per_storypoint": 6.0,
  "werkstromen": ["ops", "dev", "func", "access"]
}
```

- `uren_per_storypoint`: positief getal. De huidige adapter leest dit uit `Instellingen!B5`.
- `werkstromen`: lijst met unieke, niet-lege namen. De huidige adapter leest deze uit `Instellingen!B6`, splitst op komma's en normaliseert de namen naar kleine letters. De lijst bepaalt welke werkstroompercentages voor medewerkers uit Calc worden gelezen.

## 7. Validatie

De applicatie valideert het contract onafhankelijk van de gegevensbron. De adapter mag daarnaast brongebonden controles uitvoeren, maar is niet de enige plaats waar contractvalidatie plaatsvindt.

### 6.1 Harde fouten

- Ontbrekende of onbekende contractnaam/-versie.
- Ontbrekende verplichte top-level onderdelen.
- Ongeldige datumnotatie of ongeldige datum.
- Lege of dubbele `userid`.
- Lege of dubbele `rooster_id`.
- Onbekende medewerker- of roosterverwijzing in een toewijzing.
- Ongeldige geldigheidsperiode.
- Overlappende toewijzingen voor dezelfde medewerker.
- Ongeldig aantal weekpatronen of dagwaarden.
- Roosteruren buiten 0–9 of niet-numerieke roosteruren.
- Werkstroompercentage buiten 0–100 of niet-numeriek.
- Niet-positieve `uren_per_storypoint`.
- Dubbele combinatie `userid` + `datum` bij afwezigheden.
- Onbekende medewerker bij een afwezigheid.
- Afwezigheidscode die niet door de afgesproken codevalidatie wordt geaccepteerd.

### 6.2 Waarschuwingen

- Werkstroompercentages per medewerker tellen niet op tot 100%. De huidige functie `controleer_rolpercentages()` geeft hiervoor een waarschuwing.
- Eventuele gegevens die buiten de actieve periode van een medewerker vallen, hebben geen invloed op de berekening.

### 6.3 Aanvullende validatieregels

- Afwezigheidsrecords buiten de actieve periode van een medewerker worden genegeerd.
- Een onbekende afwezigheidscode is een harde fout.
- Agile-instellingtypen zijn beperkt tot `DagStart`, `Refinement` en `Sprintwissel`; dagafkortingen zijn beperkt tot `ma`, `di`, `wo`, `do`, `vr`.
- Roosteruren zijn gehele getallen van 0 tot en met 9.
- Onbekende extra velden zijn toegestaan als uitbreidingsvelden. De applicatie mag velden die zij niet kent negeren; ze mogen de verwerking van bekende velden niet veranderen.

## 8. Fouten en foutafhandeling

Een contractfout moet de verwerking stoppen voordat sprintresultaten worden berekend. De foutmelding moet ten minste aangeven:

- welk onderdeel ongeldig is;
- welk record of welke identificatie betrokken is;
- welke regel is geschonden.

Fouten worden machineleesbaar gerapporteerd met ten minste `foutcode`, `onderdeel`, een record-/identificatie of gegevenspad, en een begrijpelijke `omschrijving`. De adapter mag een bronfout niet stilzwijgend omzetten in een geldige lege waarde.

## 9. Applicatie-uitvoer naar SprintInfo (afzonderlijk contract)

De applicatie-SprintInfo-overdracht is een afzonderlijke interface. De huidige applicatie schrijft een lijst sprintobjecten naar `sprints.json` en start daarna `sprintinfo.py` als apart proces. Sprintdatums worden vóór serialisatie omgezet naar ISO-datums.

De berekende medewerkerresultaten bevatten momenteel:

```json
{
  "userid": "j001",
  "naam": "Jan van der Berg",
  "uren": 72.5,
  "storypoints": 12,
  "werkstromen": {
    "dev": 70,
    "ops": 20,
    "func": 10,
    "access": 0
  },
  "uren_per_werkstroom": {
    "dev": 50.75,
    "ops": 14.5,
    "func": 7.25
  },
  "storypoints_per_werkstroom": {
    "dev": 8,
    "ops": 2,
    "func": 2,
    "access": 0
  }
}
```

De huidige uitvoer bevat daarnaast per sprint `naam`, `begindatum`, `einddatum`, `agile_instellingen` en `netto_uren` (de lijst met medewerkerresultaten). Deze beschrijving legt de aangetroffen vorm vast; de volledige SprintInfo-validatie, foutafhandeling en compatibiliteitsregels worden in een afzonderlijke specificatie uitgewerkt.

## 10. Versiebeheer en compatibiliteit

- De payload bevat altijd `contract.naam` en `contract.versie`.
- De applicatie accepteert alleen expliciet ondersteunde contractversies.
- Een wijziging die bestaande velden verwijdert, hernoemt, van betekenis verandert of verplicht maakt, vereist een nieuwe contractversie.
- Uitbreidingen met optionele velden zijn binnen contractversie 2.0 toegestaan. Onbekende extra velden worden door een ontvanger genegeerd; bestaande velden behouden hun betekenis en validatieregels.
- Adapter en applicatie worden samen getest met dezelfde representatieve JSON-testbestanden.
- De contractdocumentatie in de repositories `Sprintplanner` en `LibreOffice` moet inhoudelijk identiek zijn.

## 11. Implementatiestappen

1. Dit concept inhoudelijk reviewen en de open validatiekeuzes besluiten.
2. Het contractdocument identiek vastleggen in beide repositories.
3. Een representatieve JSON-payload maken op basis van de huidige Calc-gegevens.
4. Een contractvalidator in de zelfstandige applicatielaag implementeren.
5. De LibreOffice-adapter aanpassen zodat deze JSON-contractgegevens produceert in plaats van Python-domeinobjecten rechtstreeks door te geven.
6. Een adaptercontracttest uitvoeren met representatieve gegevens.
7. De bestaande SprintInfo-interface afzonderlijk blijven testen.
8. Dezelfde contracttest later met een Excel-adapter kunnen uitvoeren.

## 12. Bekende verschillen tussen huidige implementatie en contract 2.0

| Onderwerp | Huidige situatie | Contract 2.0 |
|---|---|---|
| Adapter → applicatie | Python-objecten rechtstreeks doorgegeven | Interpreter-onafhankelijke JSON-payload; applicatie vertaalt deze naar domeinobjecten |
| Medewerkers | `Medewerker`-objecten | JSON-records met `userid`, daarna opnieuw `Medewerker`-objecten binnen de applicatie |
| Roosters | Dictionary met `Rooster`-objecten | JSON-lijst met `rooster_id`, daarna opnieuw `Rooster`-objecten binnen de applicatie |
| Toewijzingen | `Roostertoewijzing`-objecten met objectreferenties | JSON-verwijzingen via `userid` en `rooster_id`, daarna gekoppelde `Roostertoewijzing`-objecten binnen de applicatie |
| Afwezigheden | Dictionary met Python-datums als sleutels | Lijst met userid, ISO-datum en code |
| Einddatum | Ingelezen, nog niet toegepast in de berekeningen | Laatste actieve dag; daarna uitsluiten |
| Roosteruren | Domeinklasse accepteert 0–24 | Contract staat 0–9 toe |
| Werkstromenlijst | Gebruikt bij adapterinlezing, niet apart doorgegeven | Expliciet in `instellingen.werkstromen` |
| `uren_per_storypoint` | Losse waarde | Onderdeel van `instellingen` |
| Transport | Huidige directe Python-aanroep | Nog niet gekozen; contract staat los van transport |

---

**Reviewstatus:** de inhoudelijke keuzes voor de hier beschreven validatieregels en uitbreidingsvelden zijn afgestemd. Dit document is nog een ontwerp en geen bewijs dat de bestaande code al aan contract 2.0 voldoet. De implementatie moet de beschreven regels nog afdwingen.
