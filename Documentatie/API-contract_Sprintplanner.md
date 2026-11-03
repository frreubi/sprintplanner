# API-contract Sprintplanner

**Versie 1.0** \| **3 november 2026** \| Eerste vastlegging

Dit document beschrijft de communicatie tussen de LibreOffice-integratie
en de Sprintplanner-applicatie. De twee onderdelen worden afzonderlijk
ontwikkeld en beheerd in eigen Git-repositories. Het API-contract zorgt
ervoor dat beide onderdelen onafhankelijk kunnen worden aangepast,
zolang de afgesproken interface behouden blijft.

## 1. Doel

Dit document beschrijft de communicatie tussen de LibreOffice-integratie
en de Sprintplanner-applicatie. De twee onderdelen worden afzonderlijk
ontwikkeld en beheerd in eigen Git-repositories. Het API-contract zorgt
ervoor dat beide onderdelen onafhankelijk kunnen worden aangepast,
zolang de afgesproken interface behouden blijft.

## 2. Architectuur

De applicatie bestaat uit vier functionele onderdelen:

  -----------------------------------------------------------------------
  Onderdeel                           Verantwoordelijkheid
  ----------------------------------- -----------------------------------
  `sprintplanner.py`                  Communicatie met LibreOffice Calc:
                                      gegevens lezen en schrijven.

  `applicatie.py`                     Centrale coördinatie van de
                                      applicatie.

  `berekeningen.py`                   Alle bedrijfs- en
                                      planningsberekeningen.

  `sprintinfo.py`                     Presentatie en interactie met de
                                      gebruiker.
  -----------------------------------------------------------------------

Gegevensstroom bij het starten:

`LibreOffice Calc → sprintplanner.py → applicatie.py → berekeningen.py → sprintinfo.py`

De applicatie mag niet afhankelijk zijn van LibreOffice of UNO.

## 3. Startinterface

De applicatie wordt gestart vanuit de LibreOffice-adapter.

``` python
applicatie.start(gegevens)
```

De functie ontvangt één argument: `gegevens`. De applicatie is
verantwoordelijk voor de verdere verwerking en start uiteindelijk
SprintInfo.

## 4. Gegevenscontract

De parameter `gegevens` is een dictionary met de volgende structuur:

  ------------------------------------------------------------------------------------
  Sleutel                 Type                        Omschrijving
  ----------------------- --------------------------- --------------------------------
  `sprints`               `list`                      Sprintgegevens

  `medewerkers`           `list[Medewerker]`          Medewerkersobjecten

  `roosters`              `dict`                      Roosters, geïndexeerd op
                                                      rooster-ID

  `toewijzingen`          `list[Roostertoewijzing]`   Medewerker-roostertoewijzingen

  `afwezigheden`          `dict`                      Afwezigheden per medewerker

  `agile_instellingen`    `list[dict]`                Agile-overheadinstellingen

  `uren_per_storypoint`   `number`                    Aantal uren per storypoint
  ------------------------------------------------------------------------------------

### 4.1 Sprints

Iedere sprint bevat:

``` python
{"naam": str, "begindatum": date, "einddatum": date}
```

Datums worden bij binnenkomst aangeleverd als Python `date`-objecten.

### 4.2 Medewerkers

Medewerkers worden aangeleverd als instanties van de klasse
`Medewerker`. Relevante eigenschappen:

-   `userid`
-   `naam`
-   `rol`
-   `werkstromen`
-   `beheerder`
-   `access_analist`
-   `einddatum`

`werkstromen` is een dictionary met werkstroomnamen en percentages.

### 4.3 Roosters

Roosters worden aangeleverd als dictionary, waarbij de rooster-ID de
sleutel vormt. De waarden zijn instanties van de klasse `Rooster`.

### 4.4 Toewijzingen

Toewijzingen worden aangeleverd als instanties van `Roostertoewijzing`.
Een toewijzing bevat een medewerker, een rooster en een
geldigheidsperiode.

### 4.5 Afwezigheden

De structuur is:

``` python
{"userid": {date: "V", date: "4V"}}
```

De daadwerkelijke datumwaarden zijn Python `date`-objecten.

### 4.6 Agile-instellingen

Iedere instelling bevat:

``` python
{"type": str, "dagen": list, "duur": float}
```

Voorbeelden van typen zijn `DagStart`, `Refinement` en `Sprintwissel`.

### 4.7 Uren per storypoint

`uren_per_storypoint` wordt gelezen uit `Instellingen!B5` in Calc. De
waarde wordt als getal aangeleverd. De applicatie geeft deze door aan de
berekeningslaag. Er wordt geen vaste waarde in de applicatie gebruikt.

## 5. Verantwoordelijkheden en afhankelijkheden

### LibreOffice-adapter

-   Leest gegevens uit Calc.
-   Zet Calc-gegevens om naar Python-objecten.
-   Levert de gegevens aan via `applicatie.start(gegevens)`.
-   Verzorgt eventuele terugkoppeling naar Calc.

### Applicatie

-   Ontvangt de gegevens.
-   Coördineert de verwerking.
-   Roept de benodigde berekeningen aan.
-   Levert de resultaten aan SprintInfo.

### Berekeningen

-   Bevat alle bedrijfslogica.
-   Is onafhankelijk van Calc en SprintInfo.
-   Ontvangt gegevens en levert berekende resultaten terug.

### SprintInfo

-   Verzorgt de presentatie.
-   Biedt navigatie tussen sprints.
-   Presenteert netto-uren en storypoints.

## 6. Overdracht naar SprintInfo

De applicatie schrijft de sprintgegevens naar `sprints.json`. Vervolgens
wordt `sprintinfo.py` als afzonderlijk Python-proces gestart. De
sprintdatums worden vóór JSON-serialisatie omgezet naar ISO
8601-strings.

De huidige berekende gegevens per medewerker bevatten:

``` python
{
    "userid": str,
    "naam": str,
    "uren": number,
    "storypoints": int,
    "werkstromen": dict,
    "storypoints_per_werkstroom": dict
}
```

De JSON-overdracht vormt een afzonderlijke interface tussen de
applicatie en SprintInfo.

## 7. Ontwerpregels

-   De applicatie bevat geen Calc- of UNO-afhankelijkheden.
-   De berekeningen bevatten geen presentatie- of opslaglogica.
-   De adapter bevat geen bedrijfsberekeningen.
-   Werkstromen zijn dynamisch en worden niet hardcoded in de
    berekeningslogica.
-   De standaardwerkstroom is gelijk aan de formele rol wanneer een
    gelijknamige werkstroom bestaat.
-   De uren per storypoint zijn configureerbaar.
-   De applicatie is onafhankelijk van de gebruikte gegevensbron.

## 8. Wijzigingen aan het API-contract

Wijzigingen aan de gegevensstructuur of aan de startinterface moeten in
beide repositories worden beoordeeld. Bij iedere wijziging geldt:

-   Het API-contract wordt bijgewerkt.
-   De adapter en applicatie worden op compatibiliteit gecontroleerd.
-   De gegevensoverdracht wordt getest.
-   De bestaande testsuite moet slagen.

## 9. Nog te specificeren

De volgende punten zijn nog niet volledig vastgelegd:

-   De precieze foutafhandeling tussen adapter en applicatie.
-   De validatie van verplichte en optionele gegevens.
-   De versie-identificatie van het API-contract.
-   De exacte JSON-structuur die SprintInfo verwacht, inclusief
    eventuele aanvullende velden.

Deze onderdelen worden vastgelegd zodra de betreffende functionaliteit
verder is uitgewerkt.
