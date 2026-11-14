# Sprintplanner – projectupdate 14 november 2026

## Contract 3.0

De contractstructuur is gewijzigd van vaste werkstroompercentages op `Medewerker` naar een dynamisch model:

- `rollen`: rol-ID, naam, standaardwerkstroom en geldigheidsperiode.
- `medewerkers`: verwijzen rechtstreeks naar één rol-ID; geen werkstroompercentages op het medewerkerobject.
- `percentages`: percentageverdelingen met een `percentage_id` en een dynamische mapping van werkstroom-ID naar fractie (0.0–1.0).
- `toewijzingen`: één lijst met type `Rooster` of `Percentage`, plus `toewijzing_id` en geldigheidsperiode.
- Een percentage-toewijzing is optioneel; een roostertoewijzing is verplicht op iedere actieve werkdag binnen een sprint.
- Geen aparte werkstromen-sheet en geen roltoewijzingstype.

De impliciete verdelingsregel:
- Zonder expliciete percentageverdeling is de standaardwerkstroom van de rol 100%.
- Als expliciete percentages alleen andere werkstromen bevatten, vult de standaardwerkstroom het restant aan.
- Als de expliciete verdeling ook de eigen standaardwerkstroom bevat, vervangt die expliciete waarde de impliciete 100%; het restant is ander werk buiten sprintteams.
- Zonder standaardwerkstroom tellen alleen expliciete werkstromen mee.

Voorbeelden voor een OPS-medewerker:
- geen percentageverdeling: 100% OPS;
- DEV 10%: 90% OPS + 10% DEV;
- DEV 10% en FUNC 10%: 80% OPS + 10% DEV + 10% FUNC;
- OPS 80%: 80% OPS + 20% ander werk;
- OPS 80% en DEV 10%: 80% OPS + 10% DEV + 10% ander werk.

## Implementatie bijgewerkt

- `contract.py` leest contract 3.0 in en bouwt de domeinobjecten op.
- `validatie.py` telt alleen `Roostertoewijzing` als rooster en controleert maximaal één geldige percentage-toewijzing per medewerker per dag.
- `toewijzingen.py` levert `zoek_toewijzing()` als tuple `(roostertoewijzing, percentage_toewijzing_of_None)`.
- `berekeningen.py` verwerkt de tuple, berekent netto uren en verdeelt sprinturen per werkstroom volgens de rol- en percentagegegevens.
- `applicatie.py` geeft de rollen door aan de sprintresultaatberekening.
- Oude unit tests die nog een percentage-dictionary als zesde constructorargument van `Medewerker` doorgaven, zijn aangepast aan het nieuwe model.
- `Documentatie/API-contract_Sprintplanner_v3.0.md` beschrijft de actuele externe structuur en verdelingsregels. De v2.0-documentatie is behouden als historische versie.

## Teststatus

Uitgevoerd in de aangeleverde projectkopie:

`py -3.15 -m pytest -q`

Resultaat: **104 passed, 42 subtests passed**.

Alle Python-bestanden zijn ook door `compileall` gecontroleerd.

## Nog niet geverifieerd

De LibreOffice-adapter die de Calc-gegevens omzet naar contract-JSON is niet als zelfstandige broncode in deze projectmap aanwezig. `uno_client.py` roept de macro `sprintplanner.py$lever_contractbericht` uit de LibreOffice-gebruikersomgeving aan. Die macro moet nog worden aangepast zodat hij contract 3.0 produceert (rollen, percentages, getypeerde toewijzingen en de nieuwe instellingenstructuur). De geautomatiseerde tests bewijzen dus de applicatiekant, niet de volledige Calc-naar-applicatieketen.
