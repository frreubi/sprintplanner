import json
import re
from datetime import date, timedelta

from medewerker import Medewerker
from rooster import Rooster
from toewijzingen import Roostertoewijzing
from sprints import Sprint


class ContractValidatieFout(ValueError):
    def __init__(self, foutcode, onderdeel, gegevenspad, omschrijving):
        self.foutcode = foutcode
        self.onderdeel = onderdeel
        self.gegevenspad = gegevenspad
        self.omschrijving = omschrijving
        super().__init__(omschrijving)

    def als_dict(self):
        return {
            "foutcode": self.foutcode,
            "onderdeel": self.onderdeel,
            "gegevenspad": self.gegevenspad,
            "omschrijving": self.omschrijving,
        }


def _fout(code, onderdeel, pad, omschrijving):
    raise ContractValidatieFout(code, onderdeel, pad, omschrijving)


def _datum(waarde, onderdeel, pad, verplicht=True):
    if waarde is None and not verplicht:
        return None
    if not isinstance(waarde, str):
        _fout("ONGELDIGE_DATUM", onderdeel, pad, "Datum moet tekst zijn in YYYY-MM-DD-formaat.")
    try:
        parsed = date.fromisoformat(waarde)
    except ValueError:
        _fout("ONGELDIGE_DATUM", onderdeel, pad, f"Ongeldige datum: {waarde!r}.")
    if parsed.isoformat() != waarde:
        _fout("ONGELDIGE_DATUM", onderdeel, pad, f"Datum moet YYYY-MM-DD zijn: {waarde!r}.")
    return parsed


def _tekst(record, veld, onderdeel, pad, leeg_toegestaan=False):
    waarde = record.get(veld)
    if not isinstance(waarde, str) or (not leeg_toegestaan and not waarde.strip()):
        _fout("ONGELDIGE_WAARDE", onderdeel, f"{pad}.{veld}", "Verplicht tekstveld ontbreekt of is ongeldig.")
    return waarde.strip()


def _getal(waarde, onderdeel, pad, minimum=None, maximum=None, geheel=False, positief=False):
    if (
        not isinstance(waarde, (int, float))
        or isinstance(waarde, bool)
        or (geheel and not isinstance(waarde, int))
    ):
        _fout("ONGELDIG_GETAL", onderdeel, pad, "Waarde moet een geldig getal zijn.")
    if positief and waarde <= 0:
        _fout("ONGELDIG_GETAL", onderdeel, pad, "Waarde moet groter zijn dan nul.")
    if minimum is not None and waarde < minimum:
        _fout("ONGELDIG_GETAL", onderdeel, pad, f"Waarde mag niet lager zijn dan {minimum}.")
    if maximum is not None and waarde > maximum:
        _fout("ONGELDIG_GETAL", onderdeel, pad, f"Waarde mag niet hoger zijn dan {maximum}.")
    return waarde


def laad_contract(json_tekst):
    try:
        gegevens = json.loads(json_tekst)
    except (TypeError, json.JSONDecodeError) as exc:
        _fout("ONGELDIGE_JSON", "contract", "$", f"JSON kan niet worden gelezen: {exc}")

    if not isinstance(gegevens, dict):
        _fout("ONGELDIGE_STRUCTUUR", "contract", "$", "Het contract moet een JSON-object zijn.")

    contract = gegevens.get("contract")
    if not isinstance(contract, dict) or contract.get("naam") != "Sprintplanner" or contract.get("versie") != "2.0":
        _fout("CONTRACTVERSIE_NIET_ONDERSTEUND", "contract", "$.contract", "Alleen Sprintplanner-contractversie 2.0 wordt ondersteund.")

    verplicht = (
        "sprints", "medewerkers", "roosters", "toewijzingen",
        "afwezigheden", "agile_instellingen", "instellingen",
    )
    for onderdeel in verplicht:
        if onderdeel not in gegevens:
            _fout("ONDERDEEL_ONTBREEKT", onderdeel, f"$.{onderdeel}", "Verplicht contractonderdeel ontbreekt.")
        if onderdeel != "instellingen" and not isinstance(gegevens[onderdeel], list):
            _fout("ONGELDIGE_STRUCTUUR", onderdeel, f"$.{onderdeel}", "Onderdeel moet een lijst zijn.")

    instellingen_data = gegevens["instellingen"]
    if not isinstance(instellingen_data, dict):
        _fout("ONGELDIGE_STRUCTUUR", "instellingen", "$.instellingen", "Instellingen moeten een object zijn.")
    uren_per_storypoint = _getal(
        instellingen_data.get("uren_per_storypoint"), "instellingen",
        "$.instellingen.uren_per_storypoint", positief=True
    )
    werkstromen = instellingen_data.get("werkstromen")
    if (
        not isinstance(werkstromen, list)
        or not werkstromen
        or any(not isinstance(w, str) or not w.strip() for w in werkstromen)
        or len({w.strip().lower() for w in werkstromen}) != len(werkstromen)
    ):
        _fout("ONGELDIGE_WERKSTROMEN", "instellingen", "$.instellingen.werkstromen", "Werkstromen moeten een niet-lege lijst met unieke namen zijn.")
    werkstromen = [w.strip().lower() for w in werkstromen]

    sprints = []
    for i, item in enumerate(gegevens["sprints"]):
        pad = f"$.sprints[{i}]"
        if not isinstance(item, dict):
            _fout("ONGELDIGE_STRUCTUUR", "sprints", pad, "Sprint moet een object zijn.")
        begin = _datum(item.get("begindatum"), "sprints", f"{pad}.begindatum")
        eind = _datum(item.get("einddatum"), "sprints", f"{pad}.einddatum")
        if eind < begin:
            _fout("ONGELDIGE_PERIODE", "sprints", pad, "Einddatum ligt vóór begindatum.")
        sprints.append(Sprint(_tekst(item, "naam", "sprints", pad), begin, eind))

    medewerkers = []
    medewerkers_op_id = {}
    for i, item in enumerate(gegevens["medewerkers"]):
        pad = f"$.medewerkers[{i}]"
        if not isinstance(item, dict):
            _fout("ONGELDIGE_STRUCTUUR", "medewerkers", pad, "Medewerker moet een object zijn.")
        userid = _tekst(item, "userid", "medewerkers", pad)
        if userid in medewerkers_op_id:
            _fout("DUBBEL_USERID", "medewerkers", f"{pad}.userid", f"Userid {userid!r} komt meer dan eenmaal voor.")
        percentages = item.get("werkstromen")
        if not isinstance(percentages, dict):
            _fout("ONGELDIGE_WERKSTROMEN", "medewerkers", f"{pad}.werkstromen", "Werkstromen moeten een object zijn.")
        if set(percentages) != set(werkstromen):
            _fout("WERKSTROOMAFWIJKING", "medewerkers", f"{pad}.werkstromen", "Werkstroomnamen moeten overeenkomen met instellingen.werkstromen.")
        for naam, percentage in percentages.items():
            _getal(percentage, "medewerkers", f"{pad}.werkstromen.{naam}", 0, 100)
        startdatum = _datum(
            item.get("startdatum", "2025-01-01"),
            "medewerkers",
            f"{pad}.startdatum",
        )
        einddatum = _datum(item.get("einddatum"), "medewerkers", f"{pad}.einddatum", verplicht=False)
        if einddatum is not None and einddatum < startdatum:
            _fout("ONGELDIGE_PERIODE", "medewerkers", pad, "Einddatum ligt vóór startdatum.")
        try:
            medewerker = Medewerker(
                userid,
                _tekst(item, "voornaam", "medewerkers", pad),
                _tekst(item, "tussenvoegsel", "medewerkers", pad, leeg_toegestaan=True),
                _tekst(item, "achternaam", "medewerkers", pad),
                _tekst(item, "rol", "medewerkers", pad),
                percentages,
                item.get("beheerder"),
                item.get("access_analist"),
                einddatum,
                startdatum,
            )
        except (TypeError, ValueError) as exc:
            _fout("ONGELDIGE_MEDEWERKER", "medewerkers", pad, str(exc))
        medewerkers.append(medewerker)
        medewerkers_op_id[userid] = medewerker

    roosters = {}
    for i, item in enumerate(gegevens["roosters"]):
        pad = f"$.roosters[{i}]"
        if not isinstance(item, dict):
            _fout("ONGELDIGE_STRUCTUUR", "roosters", pad, "Rooster moet een object zijn.")
        rooster_id = _tekst(item, "rooster_id", "roosters", pad)
        if rooster_id in roosters:
            _fout("DUBBEL_ROOSTER_ID", "roosters", f"{pad}.rooster_id", f"Rooster-ID {rooster_id!r} komt meer dan eenmaal voor.")
        cyclus = item.get("cyclus_weken")
        if type(cyclus) is not int or cyclus not in (1, 2):
            _fout("ONGELDIGE_CYCLUS", "roosters", f"{pad}.cyclus_weken", "Cyclus moet 1 of 2 zijn.")
        weken = item.get("uren_per_week")
        if not isinstance(weken, list) or len(weken) != cyclus:
            _fout("ONGELDIGE_ROOSTERSTRUCTUUR", "roosters", f"{pad}.uren_per_week", "Aantal weekpatronen moet overeenkomen met de cyclus.")
        for weeknr, week in enumerate(weken):
            if not isinstance(week, list) or len(week) != 5:
                _fout("ONGELDIGE_ROOSTERSTRUCTUUR", "roosters", f"{pad}.uren_per_week[{weeknr}]", "Een weekpatroon moet vijf werkdagen bevatten.")
            for dag, uren in enumerate(week):
                _getal(uren, "roosters", f"{pad}.uren_per_week[{weeknr}][{dag}]", 0, 9, geheel=True)
        roosters[rooster_id] = Rooster(rooster_id, cyclus, weken)

    toewijzingen = []
    per_medewerker = {userid: [] for userid in medewerkers_op_id}
    for i, item in enumerate(gegevens["toewijzingen"]):
        pad = f"$.toewijzingen[{i}]"
        if not isinstance(item, dict):
            _fout("ONGELDIGE_STRUCTUUR", "toewijzingen", pad, "Toewijzing moet een object zijn.")
        userid = _tekst(item, "userid", "toewijzingen", pad)
        rooster_id = _tekst(item, "rooster_id", "toewijzingen", pad)
        if userid not in medewerkers_op_id:
            _fout("ONBEKENDE_MEDEWERKER", "toewijzingen", f"{pad}.userid", f"Onbekende medewerker: {userid}.")
        if rooster_id not in roosters:
            _fout("ONBEKEND_ROOSTER", "toewijzingen", f"{pad}.rooster_id", f"Onbekend rooster: {rooster_id}.")
        begin = _datum(item.get("geldig_vanaf"), "toewijzingen", f"{pad}.geldig_vanaf")
        eind = _datum(item.get("geldig_tm"), "toewijzingen", f"{pad}.geldig_tm", verplicht=False)
        if eind is not None and eind < begin:
            _fout("ONGELDIGE_PERIODE", "toewijzingen", pad, "geldig_tm ligt vóór geldig_vanaf.")
        toewijzing = Roostertoewijzing(medewerkers_op_id[userid], roosters[rooster_id], begin, eind)
        toewijzingen.append(toewijzing)
        per_medewerker[userid].append(toewijzing)

    for userid, items in per_medewerker.items():
        items.sort(key=lambda t: t.geldig_vanaf)
        for vorige, volgende in zip(items, items[1:]):
            if vorige.geldig_tm is None or volgende.geldig_vanaf <= vorige.geldig_tm:
                _fout("OVERLAPPENDE_TOEWIJZING", "toewijzingen", f"$.toewijzingen[{userid}]", f"Toewijzingen voor {userid} overlappen.")

    for sprint in sprints:
        for medewerker in medewerkers:
            eerste_dag = max(sprint.begindatum, medewerker.startdatum)
            laatste_dag = min(
                sprint.einddatum,
                medewerker.einddatum if medewerker.einddatum is not None else sprint.einddatum,
            )
            dag = eerste_dag

            while dag <= laatste_dag:
                if dag.weekday() < 5:
                    geldig = [
                        t for t in per_medewerker[medewerker.userid]
                        if t.geldt_op(dag)
                    ]

                    if len(geldig) != 1:
                        _fout(
                            "ROOSTERTOEWIJZING_ONTBREEKT" if not geldig else "MEERDERE_ROOSTERTOEWIJZINGEN",
                            "toewijzingen",
                            f"$.toewijzingen[{medewerker.userid}].{dag.isoformat()}",
                            f"Medewerker {medewerker.userid} moet op {dag.isoformat()} precies één roostertoewijzing hebben.",
                        )

                dag += timedelta(days=1)

    afwezigheden = {}
    patroon = re.compile(r"^(?:[1-9][0-9]*)?[VBCZ]$")
    for i, item in enumerate(gegevens["afwezigheden"]):
        pad = f"$.afwezigheden[{i}]"
        if not isinstance(item, dict):
            _fout("ONGELDIGE_STRUCTUUR", "afwezigheden", pad, "Afwezigheid moet een object zijn.")
        userid = _tekst(item, "userid", "afwezigheden", pad)
        if userid not in medewerkers_op_id:
            _fout("ONBEKENDE_MEDEWERKER", "afwezigheden", f"{pad}.userid", f"Onbekende medewerker: {userid}.")
        datum = _datum(item.get("datum"), "afwezigheden", f"{pad}.datum")
        code = _tekst(item, "code", "afwezigheden", pad).upper()
        if not patroon.fullmatch(code):
            _fout("ONGELDIGE_AFWEZIGHEIDSCODE", "afwezigheden", f"{pad}.code", f"Onbekende afwezigheidscode: {code}.")
        if datum in afwezigheden.setdefault(userid, {}):
            _fout("DUBBELE_AFWEZIGHEID", "afwezigheden", pad, f"Medewerker {userid} heeft meer dan één afwezigheid op {datum}.")
        medewerker = medewerkers_op_id[userid]
        if (
            medewerker.startdatum <= datum
            and (medewerker.einddatum is None or datum <= medewerker.einddatum)
        ):
            afwezigheden[userid][datum] = code

    agile_instellingen = []
    toegestane_types = {"DagStart", "Refinement", "Sprintwissel"}
    toegestane_dagen = {"ma", "di", "wo", "do", "vr"}
    for i, item in enumerate(gegevens["agile_instellingen"]):
        pad = f"$.agile_instellingen[{i}]"
        if not isinstance(item, dict):
            _fout("ONGELDIGE_STRUCTUUR", "agile_instellingen", pad, "Agile-instelling moet een object zijn.")
        type_ = _tekst(item, "type", "agile_instellingen", pad)
        if type_ not in toegestane_types:
            _fout("ONGELDIG_AGILE_TYPE", "agile_instellingen", f"{pad}.type", f"Onbekend agile-type: {type_}.")
        dagen = item.get("dagen")
        if not isinstance(dagen, list) or any(dag not in toegestane_dagen for dag in dagen):
            _fout("ONGELDIGE_AGILE_DAGEN", "agile_instellingen", f"{pad}.dagen", "Dagen moeten ma, di, wo, do of vr zijn.")
        duur = _getal(item.get("duur"), "agile_instellingen", f"{pad}.duur", positief=True)
        agile_instellingen.append({"type": type_, "dagen": dagen, "duur": duur})

    return {
        "sprints": sprints,
        "medewerkers": medewerkers,
        "roosters": roosters,
        "toewijzingen": toewijzingen,
        "afwezigheden": afwezigheden,
        "agile_instellingen": agile_instellingen,
        "uren_per_storypoint": uren_per_storypoint,
        "werkstromen": werkstromen,
    }
