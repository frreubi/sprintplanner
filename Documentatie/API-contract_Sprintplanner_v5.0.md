# API-contract Sprintplanner

**Versie:** 5.0  
**Status:** geïmplementeerd in `contract.py`; adapterimplementatie moet dit contract leveren.  
**Doel:** interpreter-onafhankelijke gegevensuitwisseling tussen een gegevensbronadapter en de Sprintplanner-applicatie.

## 1. Architectuur

De adapter leest en schrijft de gegevensbron en vertaalt die naar dit JSON-contract. De applicatie valideert het bericht en bouwt domeinobjecten op. De bedrijfslogica en berekeningen werken met die objecten en zijn onafhankelijk van LibreOffice, UNO en de Python-runtime van de adapter.

```text
LibreOffice Calc ── LibreOffice-adapter ──┐
                                         ├── Contract 5.0 (JSON) ── Applicatie ── Berekeningen
Excel ───────────── Excel-adapter ────────┘                                  │
                                                                             └── SprintInfo-contract
```

Het SprintInfo-uitvoerformaat is een afzonderlijke interface en maakt geen deel uit van dit invoercontract.

## 2. Top-level structuur

Alle onderstaande onderdelen zijn verplicht. Lijsten mogen leeg zijn als er geen records zijn.

```json
{
  "contract": {"naam": "Sprintplanner", "versie": "5.0"},
  "rollen": [],
  "medewerkers": [],
  "roosters": [],
  "percentages": [],
  "toewijzingen": [],
  "afwezigheden": [],
  "agile_instellingen": [],
  "instellingen": {
    "standaard_sprintduur": 3,
    "datum_eerste_sprint": "2026-01-05",
    "storypoints_accessman_rapportage": 4,
    "uren_per_storypoint": 6.0
  }
}
```

`instellingen` bevat de sprint- en berekeningsinstellingen:
- `standaard_sprintduur`: positief geheel aantal weken.
- `datum_eerste_sprint`: ISO-datum; de sprintkalender wordt hiermee door de applicatie gegenereerd.
- `storypoints_accessman_rapportage`: positief geheel getal.
- `uren_per_storypoint`: positief getal.

Sprints zijn geen onderdeel van het JSON-invoercontract. De applicatie genereert de sprintkalender op basis van `standaard_sprintduur` en `datum_eerste_sprint`.

## 3. Algemene representatieregels

- JSON is UTF-8.
- Datums zijn ISO-datums in `YYYY-MM-DD`-notatie.
- Een ontbrekende optionele einddatum is `null`.
- Booleans zijn JSON `true` of `false`.
- Getallen zijn JSON-nummers, geen numerieke strings.
- Identificaties zijn tekst.
- Onbekende uitbreidingsvelden worden genegeerd.
- Werkstroom- en rol-ID's worden bij het inlezen naar kleine letters genormaliseerd.

## 4. Gegevensonderdelen

### 4.1 Gegenereerde sprints (geen contractonderdeel)

De applicatie genereert sprints intern met `genereer_sprints()`, op basis van `instellingen.datum_eerste_sprint` en `instellingen.standaard_sprintduur`. Sprints worden dus niet door de adapter aangeleverd en komen niet voor als top-level veld in het JSON-contract.

Een gegenereerde sprint bevat intern een begin- en einddatum. Beide datums tellen mee.

### 4.2 Rollen

Een rol bevat:

```json
{
  "rol_id": "dev",
  "naam": "Developer",
  "doet_sprintwerk": true,
  "geldig_vanaf": "2025-01-01",
  "geldig_tm": null
}
```

- `rol_id`: unieke, niet-lege tekst.
- `naam`: niet-lege tekst.
- `doet_sprintwerk`: boolean. `true` betekent dat de rol sprintwerk uitvoert; `false` betekent dat de rol geen sprintwerk uitvoert.

De standaardwerkstroom wordt bij het inlezen afgeleid van de rolnaam: bij `true` is de genormaliseerde rolnaam de standaardwerkstroom; bij `false` is er geen standaardwerkstroom (`None`). De standaardwerkstroom is dus geen afzonderlijk veld in het JSON-contract.
- `geldig_vanaf`: verplichte ISO-datum.
- `geldig_tm`: ISO-datum of `null`.

De medewerker verwijst rechtstreeks naar een rol via `medewerkers[].rol`. Er bestaat geen afzonderlijk roltoewijzingstype in `toewijzingen`.

### 4.3 Medewerkers

Een medewerker bevat:

```json
{
  "userid": "j001",
  "voornaam": "Jan",
  "tussenvoegsel": "van der",
  "achternaam": "Berg",
  "rol": "dev",
  "beheerder": false,
  "access_analist": false,
  "startdatum": "2025-01-01",
  "einddatum": null
}
```

- `userid`: unieke, niet-lege tekst.
- `voornaam` en `achternaam`: niet-lege tekst.
- `tussenvoegsel`: tekst; lege tekst is toegestaan.
- `rol`: verwijzing naar een bestaande `rol_id`.
- `beheerder` en `access_analist`: booleans; standaard `false` als ze ontbreken.
- `startdatum`: ISO-datum; standaard `2025-01-01` als deze ontbreekt.
- `einddatum`: ISO-datum of `null`.

De medewerker heeft één rol. Het standaardwerkstroompercentage van die rol is impliciet 100%; dit wordt niet als percentageverdeling opgeslagen.

### 4.4 Roosters

Een rooster bevat:

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

- `rooster_id`: unieke, niet-lege tekst.
- `cyclus_weken`: integer `1` of `2`.
- `uren_per_week`: precies zoveel weekpatronen als de cyclus aangeeft.
- Elk patroon bevat vijf gehele getallen, maandag tot en met vrijdag.
- Per dag is 0 tot en met 9 uur toegestaan.

Bij een cyclus van twee weken wordt patroon 1 gebruikt voor oneven ISO-weeknummers en patroon 2 voor even ISO-weeknummers.

### 4.5 Percentageverdelingen

Een percentageverdeling bevat:

```json
{
  "percentage_id": "P001",
  "verdeling": {
    "dev": 0.5,
    "func": 0.2
  }
}
```

- `percentage_id`: unieke, niet-lege tekst.
- `verdeling`: niet-leeg object met werkstroom-ID's als sleutels en fracties als waarden.
- Iedere expliciete fractie is groter dan 0 en maximaal 1.
- De som van de expliciete fracties mag niet groter zijn dan 1.
- Fracties worden als getallen van 0.0 tot en met 1.0 opgeslagen, niet als 0 tot en met 100.

Alleen afwijkingen worden opgeslagen. Er wordt dus geen standaardverdeling van 100% vastgelegd als die al uit de rol volgt.

### 4.6 Toewijzingen

Een toewijzing bevat:

```json
{
  "userid": "j001",
  "type": "Percentage",
  "toewijzing_id": "P001",
  "geldig_vanaf": "2026-01-01",
  "geldig_tm": null
}
```

`type` is `Rooster` of `Percentage`. `toewijzing_id` verwijst afhankelijk van het type naar een `rooster_id` of `percentage_id`.

De geldigheidsperiode is inclusief begin- en einddatum. `geldig_tm` mag niet vóór `geldig_vanaf` liggen.

Per medewerker geldt op een datum:
- precies één geldige roostertoewijzing;
- maximaal één geldige percentage-toewijzing.

Een percentage-toewijzing is optioneel. Zonder percentage-toewijzing geldt de impliciete 100% van de standaardwerkstroom van de rol.

Een ontbrekende roostertoewijzing en overlappende toewijzingen worden door de sprintvalidatie gemeld. Een gat tussen twee roosterperiodes is toegestaan in het contract; de validatie beoordeelt of het gat binnen een sprint valt.

### 4.7 Werkstroomverdeling voor berekeningen

De rol bepaalt de standaardwerkstroom. De expliciete percentageverdeling wordt als volgt toegepast:

1. Begin met 100% voor de standaardwerkstroom van de rol.
2. Als de expliciete verdeling de standaardwerkstroom niet bevat, worden de expliciete percentages aan andere werkstromen toegewezen en vult de standaardwerkstroom het restant aan.
3. Als de expliciete verdeling de standaardwerkstroom wél bevat, vervangt dat percentage de impliciete 100%. Het niet toegewezen restant is ander werk buiten de sprintteams.
4. Als de rol geen standaardwerkstroom heeft, worden alleen expliciet toegewezen werkstromen aan sprintwerk toegerekend.

Voorbeelden voor een medewerker met standaardwerkstroom `ops`:

| Expliciete verdeling | Resultaat |
|---|---|
| Geen percentage-toewijzing | 100% ops |
| `dev: 0.10` | 90% ops, 10% dev |
| `dev: 0.10`, `func: 0.10` | 80% ops, 10% dev, 10% func |
| `ops: 0.80` | 80% ops, 20% ander werk |
| `ops: 0.80`, `dev: 0.10` | 80% ops, 10% dev, 10% ander werk |

Het restant buiten sprintwerk wordt niet automatisch aan een andere werkstroom toegekend.

### 4.8 Afwezigheden

Een afwezigheid bevat:

```json
{"userid": "j001", "datum": "2026-11-03", "code": "4V"}
```

`userid` verwijst naar een medewerker. `datum` is een ISO-datum. `code` is tekst. De combinatie `userid` + `datum` mag maximaal eenmaal voorkomen. De contractlader bewaart de code; de sprintvalidatie controleert de geldigheid.

De berekeningen herkennen `V`, `B`, `C` en `Z` als volledige afwezigheid van de roosteruren. Een code zoals `4V` betekent vier afwezigheidsuren.

### 4.9 Agile-instellingen

Een agile-instelling bevat bijvoorbeeld:

```json
{
  "type": "DagStart",
  "ma": true,
  "di": true,
  "wo": false,
  "do": true,
  "vr": false,
  "duur": 0.5
}
```

Toegestane typen zijn `DagStart`, `Refinement` en `Sprintwissel`.

Elke instelling bevat de vijf verplichte dagvelden `ma`, `di`, `wo`, `do` en `vr`. Elk veld is een JSON-boolean (`true` of `false`). De dagen worden dus niet meer als lijst of kommagescheiden tekst aangeleverd.

`duur` is een positief getal. De vijf dagvelden en `duur` staan onafhankelijk van het type in ieder Agile-instellingsrecord.

## 5. Resultaat

De applicatie bouwt domeinobjecten op voor sprints, rollen, medewerkers, roosters, percentageverdelingen en toewijzingen. De JSON-structuur is alleen de externe representatie; de berekeningen werken met de domeinobjecten.

Het uitvoerbericht voor SprintInfo is een aparte interface. De huidige uitvoer bevat onder meer netto uren, uren per werkstroom en storypoints per werkstroom.


### Calc-adapter: werkbladindeling

Het Calc-werkblad `Toewijzingen` bevat vier kolommen:

| Kolom | Inhoud |
|---|---|
| A | Userid |
| B | Toewijzing-ID |
| C | Geldig vanaf (verplicht) |
| D | Geldig t/m (optioneel; leeg betekent geen einddatum) |

De adapter leidt het type af uit de eerste letter van `Toewijzing-ID`: `R` verwijst naar een rooster en `P` naar een percentageverdeling. Het JSON-contract bevat nog steeds expliciet `type`, zodat de externe gegevensstructuur ondubbelzinnig blijft.
