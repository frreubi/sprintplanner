from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR
from datetime import date, timedelta
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Domein.toewijzingen import zoek_toewijzing, Roostertoewijzing


def bereken_roosteruren(medewerkers, startdatum, einddatum, toewijzingen):
    if einddatum < startdatum:
        raise ValueError("De einddatum ligt voor de startdatum.")

    resultaten = []
    for medewerker in medewerkers:
        totaal_uren = 0
        datum = startdatum
        while datum <= einddatum:
            rooster_toewijzing, _ = zoek_toewijzing(
                medewerker, datum, toewijzingen
            )
            totaal_uren += rooster_toewijzing.rooster.uren_op(datum)
            datum += timedelta(days=1)
        resultaten.append([
            medewerker.userid,
            medewerker.naam,
            totaal_uren,
        ])
    return resultaten


def bereken_afwezigheidsuren(code, roosteruren):
    code = code.strip().upper()

    if code in ("V", "B", "C", "Z"):
        return roosteruren

    if code.endswith(("V", "B", "C", "Z")):
        return int(code[:-1])

    raise ValueError(f"Ongeldige afwezigheidscode: {code}")


def bereken_netto_uren(roosteruren, code):
    if code is None:
        return roosteruren
    afwezigheidsuren = bereken_afwezigheidsuren(code, roosteruren)
    return roosteruren - afwezigheidsuren


def bereken_netto_uren_per_periode(rooster, startdatum, einddatum, afwezigheid):
    if einddatum < startdatum:
        raise ValueError("De einddatum ligt voor de startdatum.")

    totaal_uren = 0
    datum = startdatum

    while datum <= einddatum:
        roosteruren = rooster.uren_op(datum)
        code = afwezigheid.get(datum)
        totaal_uren += bereken_netto_uren(roosteruren, code)
        datum += timedelta(days=1)

    return totaal_uren


def bereken_netto_uren_medewerkers(
    medewerkers, startdatum, einddatum, afwezigheden,
    toewijzingen, agile_instellingen
):
    if einddatum < startdatum:
        raise ValueError("De einddatum ligt voor de startdatum.")

    feestdagen = set()
    for jaar in range(startdatum.year, einddatum.year + 1):
        feestdagen.update(bereken_feestdagen(jaar))

    resultaten = []

    for medewerker in medewerkers:
        afwezigheid = afwezigheden.get(medewerker.userid, {})
        netto_uren = 0
        werkzaam = False
        datum = max(startdatum, medewerker.startdatum)
        laatste_dag = min(
            einddatum,
            medewerker.einddatum if medewerker.einddatum is not None else einddatum,
        )

        while datum <= laatste_dag:
            roosters = [
                t for t in toewijzingen
                if isinstance(t, Roostertoewijzing)
                and t.medewerker is medewerker
                and t.geldt_op(datum)
            ]

            if roosters:
                rooster_toewijzing, _ = zoek_toewijzing(
                    medewerker, datum, toewijzingen
                )
                werkzaam = True
                roosteruren = rooster_toewijzing.rooster.uren_op(datum)

                if datum not in feestdagen:
                    beschikbare_uren = bereken_netto_uren(
                        roosteruren, afwezigheid.get(datum)
                    )
                    overhead = bereken_agile_overhead_per_dag(
                        medewerker, datum, startdatum,
                        toewijzingen, agile_instellingen,
                        beschikbare_uren
                    )
                    netto_uren += beschikbare_uren - overhead

            datum += timedelta(days=1)

        if werkzaam:
            resultaten.append([medewerker.userid, medewerker.naam, netto_uren])

    return resultaten


def bereken_feestdagen(jaar):
    a = jaar % 19
    b = jaar // 100
    c = jaar % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    maand = (h + l - 7 * m + 114) // 31
    dag = (h + l - 7 * m + 114) % 31 + 1
    pasen = date(jaar, maand, dag)

    return {
        date(jaar, 1, 1),
        pasen,
        pasen + timedelta(days=1),
        date(jaar, 4, 27),
        date(jaar, 5, 5),
        pasen + timedelta(days=39),
        pasen + timedelta(days=49),
        pasen + timedelta(days=50),
        date(jaar, 12, 25),
        date(jaar, 12, 26),
    }

def bereken_agile_overhead_per_dag(
    medewerker, datum, startdatum, toewijzingen,
    agile_instellingen, beschikbare_uren
):
    dag = ("ma", "di", "wo", "do", "vr", "za", "zo")[datum.weekday()]
    roosters = [
        t for t in toewijzingen
        if isinstance(t, Roostertoewijzing)
        and t.medewerker is medewerker
        and t.geldt_op(datum)
    ]
    if len(roosters) != 1:
        return 0

    roosteruren = roosters[0].rooster.uren_op(datum)
    dag_overhead = 0
    sprintwissel = datum == startdatum and roosteruren > 0

    for instelling in agile_instellingen:
        if instelling["type"] == "Sprintwissel":
            if sprintwissel:
                dag_overhead += instelling["duur"]
        elif dag in ("ma", "di", "wo", "do", "vr") and instelling[dag]:
            if instelling["type"] == "DagStart" and sprintwissel:
                continue
            dag_overhead += instelling["duur"]

    return min(dag_overhead, beschikbare_uren)


def bereken_storypoints(standaard_werkstroom, netto_uren, werkstromen, uren_per_storypoint):
    if uren_per_storypoint <= 0:
        raise ValueError("Uren per storypoint moet groter zijn dan nul.")

    percentages = {
        naam.strip().lower(): Decimal(str(percentage))
        for naam, percentage in werkstromen.items()
    }

    if standaard_werkstroom is not None and standaard_werkstroom not in percentages:
        raise ValueError("Onbekende standaard werkstroom.")
    
    if any(p < 0 for p in percentages.values()):
        raise ValueError("Rolpercentages mogen niet negatief zijn.")

    totaal_percentage = sum(percentages.values())

    if totaal_percentage == 0:
        return {"totaal": 0, **dict.fromkeys(percentages, 0)}

    sprinturen = Decimal(str(netto_uren)) * totaal_percentage / 100

    totaal = int(
        (sprinturen / Decimal(str(uren_per_storypoint)))
        .quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )

    verdeling = {}

    for werkstroom, percentage in percentages.items():
        exact = Decimal(totaal) * percentage / totaal_percentage
        verdeling[werkstroom] = int(
            exact.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )

    verschil = totaal - sum(verdeling.values())

    actieve_rollen = {
        werkstroom: percentage
        for werkstroom, percentage in percentages.items()
        if percentage > 0
    }

    if verschil > 0:
        if standaard_werkstroom in actieve_rollen:
            verdeling[standaard_werkstroom] += verschil
        else:
            grootste = max(actieve_rollen, key=actieve_rollen.get)
            verdeling[grootste] += verschil
    elif verschil < 0:
        kandidaten = {
            werkstroom: percentage
            for werkstroom, percentage in actieve_rollen.items()
            if werkstroom != standaard_werkstroom
        }

        if kandidaten:
            grootste = max(kandidaten, key=kandidaten.get)
        else:
            grootste = max(actieve_rollen, key=actieve_rollen.get)

        verdeling[grootste] += verschil

    return {"totaal": totaal, **verdeling}


def _werkstroompercentages(rol, percentage_toewijzing):
    standaard = rol.standaardwerkstroom
    expliciet = (
        percentage_toewijzing.percentageverdeling.verdeling
        if percentage_toewijzing is not None
        else {}
    )

    if standaard in expliciet:
        return dict(expliciet)

    verdeling = dict(expliciet)
    if standaard is not None:
        verdeling[standaard] = 1 - sum(expliciet.values())
    return verdeling


def bereken_sprintresultaten(
    medewerkers, startdatum, einddatum, afwezigheden,
    toewijzingen, agile_instellingen, uren_per_storypoint, rollen
):
    netto_resultaten = bereken_netto_uren_medewerkers(
        medewerkers, startdatum, einddatum, afwezigheden,
        toewijzingen, agile_instellingen,
    )
    netto_per_id = {
        userid: (naam, uren) for userid, naam, uren in netto_resultaten
    }

    resultaten = []
    feestdagen = set()
    for jaar in range(startdatum.year, einddatum.year + 1):
        feestdagen.update(bereken_feestdagen(jaar))

    for medewerker in medewerkers:
        if medewerker.userid not in netto_per_id:
            continue

        naam, netto_uren = netto_per_id[medewerker.userid]
        rol = rollen[medewerker.rol]
        uren_per_werkstroom = {}
        datum = max(startdatum, medewerker.startdatum)
        laatste_dag = min(
            einddatum,
            medewerker.einddatum if medewerker.einddatum is not None else einddatum,
        )

        while datum <= laatste_dag:
            if datum.weekday() < 5 and datum not in feestdagen:
                roosters = [
                    t for t in toewijzingen
                    if isinstance(t, Roostertoewijzing)
                    and t.medewerker is medewerker
                    and t.geldt_op(datum)
                ]
                if len(roosters) == 1:
                    roosteruren = roosters[0].rooster.uren_op(datum)
                    code = afwezigheden.get(medewerker.userid, {}).get(datum)
                    beschikbare_uren = bereken_netto_uren(roosteruren, code)
                    overhead = bereken_agile_overhead_per_dag(
                        medewerker, datum, startdatum, toewijzingen,
                        agile_instellingen, beschikbare_uren,
                    )
                    sprinturen = beschikbare_uren - overhead
                    percentage_toewijzing = next((
                        t for t in toewijzingen
                        if t.medewerker is medewerker
                        and not isinstance(t, Roostertoewijzing)
                        and t.geldt_op(datum)
                    ), None)
                    verdeling = _werkstroompercentages(
                        rol, percentage_toewijzing
                    )
                    for werkstroom, fractie in verdeling.items():
                        uren_per_werkstroom[werkstroom] = (
                            uren_per_werkstroom.get(werkstroom, 0)
                            + sprinturen * fractie
                        )
            datum += timedelta(days=1)

        totaal_sprinturen = sum(uren_per_werkstroom.values())
        percentages = {
            werkstroom: uren / netto_uren * 100
            for werkstroom, uren in uren_per_werkstroom.items()
        } if netto_uren else {
            werkstroom: 0 for werkstroom in uren_per_werkstroom
        }
        storypoints = bereken_storypoints(
            rol.standaardwerkstroom,
            netto_uren,
            percentages,
            uren_per_storypoint,
        )

        resultaten.append({
            "userid": medewerker.userid,
            "naam": naam,
            "uren": netto_uren,
            "storypoints": storypoints["totaal"],
            "werkstromen": percentages,
            "uren_per_werkstroom": {
                werkstroom: round(uren, 2)
                for werkstroom, uren in uren_per_werkstroom.items()
            },
            "storypoints_per_werkstroom": {
                werkstroom: punten
                for werkstroom, punten in storypoints.items()
                if werkstroom != "totaal"
            },
        })

    return resultaten
