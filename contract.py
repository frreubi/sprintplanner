import json
from datetime import date

from medewerker import Medewerker
from rooster import Rooster
from rollen import Rol
from percentages import Percentageverdeling
from toewijzingen import Roostertoewijzing, PercentageToewijzing
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
    if not isinstance(contract, dict) or contract.get("naam") != "Sprintplanner" or contract.get("versie") != "3.0":
        _fout("CONTRACTVERSIE_NIET_ONDERSTEUND", "contract", "$.contract", "Alleen Sprintplanner-contractversie 3.0 wordt ondersteund.")

    verplicht = (
        "sprints", "rollen", "medewerkers", "roosters", "percentages",
        "toewijzingen", "afwezigheden", "agile_instellingen", "instellingen",
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

    rollen = {}
    for i, item in enumerate(gegevens["rollen"]):
        pad = f"$.rollen[{i}]"
        if not isinstance(item, dict):
            _fout("ONGELDIGE_STRUCTUUR", "rollen", pad, "Rol moet een object zijn.")
        rol_id = _tekst(item, "rol_id", "rollen", pad).lower()
        if rol_id in rollen:
            _fout("DUBBEL_ROL_ID", "rollen", f"{pad}.rol_id", f"Rol-ID {rol_id!r} komt meer dan eenmaal voor.")
        naam = _tekst(item, "naam", "rollen", pad)
        standaardwerkstroom = item.get("standaardwerkstroom")
        if standaardwerkstroom is not None:
            if not isinstance(standaardwerkstroom, str) or not standaardwerkstroom.strip():
                _fout("ONGELDIGE_WAARDE", "rollen", f"{pad}.standaardwerkstroom", "Standaardwerkstroom moet tekst zijn of null.")
            standaardwerkstroom = standaardwerkstroom.strip().lower()
        begin = _datum(item.get("geldig_vanaf"), "rollen", f"{pad}.geldig_vanaf")
        eind = _datum(item.get("geldig_tm"), "rollen", f"{pad}.geldig_tm", verplicht=False)
        if eind is not None and eind < begin:
            _fout("ONGELDIGE_PERIODE", "rollen", pad, "geldig_tm ligt vóór geldig_vanaf.")
        try:
            rollen[rol_id] = Rol(rol_id, naam, standaardwerkstroom, begin, eind)
        except (TypeError, ValueError) as exc:
            _fout("ONGELDIGE_ROL", "rollen", pad, str(exc))

    medewerkers = []
    medewerkers_op_id = {}
    for i, item in enumerate(gegevens["medewerkers"]):
        pad = f"$.medewerkers[{i}]"
        if not isinstance(item, dict):
            _fout("ONGELDIGE_STRUCTUUR", "medewerkers", pad, "Medewerker moet een object zijn.")
        userid = _tekst(item, "userid", "medewerkers", pad)
        if userid in medewerkers_op_id:
            _fout("DUBBEL_USERID", "medewerkers", f"{pad}.userid", f"Userid {userid!r} komt meer dan eenmaal voor.")
        rol_id = _tekst(item, "rol", "medewerkers", pad).lower()
        if rol_id not in rollen:
            _fout("ONBEKENDE_ROL", "medewerkers", f"{pad}.rol", f"Onbekende rol: {rol_id}.")
        startdatum = _datum(item.get("startdatum", "2025-01-01"), "medewerkers", f"{pad}.startdatum")
        einddatum = _datum(item.get("einddatum"), "medewerkers", f"{pad}.einddatum", verplicht=False)
        if einddatum is not None and einddatum < startdatum:
            _fout("ONGELDIGE_PERIODE", "medewerkers", pad, "Einddatum ligt vóór startdatum.")
        beheerder = item.get("beheerder", False)
        access_analist = item.get("access_analist", False)
        if not isinstance(beheerder, bool):
            _fout("ONGELDIGE_WAARDE", "medewerkers", f"{pad}.beheerder", "Beheerder moet True of False zijn.")
        if not isinstance(access_analist, bool):
            _fout("ONGELDIGE_WAARDE", "medewerkers", f"{pad}.access_analist", "AccessAnalist moet True of False zijn.")
        try:
            medewerker = Medewerker(
                userid=userid,
                voornaam=_tekst(item, "voornaam", "medewerkers", pad),
                tussenvoegsel=_tekst(item, "tussenvoegsel", "medewerkers", pad, leeg_toegestaan=True),
                achternaam=_tekst(item, "achternaam", "medewerkers", pad),
                rol=rol_id,
                beheerder=beheerder,
                access_analist=access_analist,
                einddatum=einddatum,
                startdatum=startdatum,
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
        try:
            roosters[rooster_id] = Rooster(rooster_id, cyclus, weken)
        except (TypeError, ValueError) as exc:
            _fout("ONGELDIG_ROOSTER", "roosters", pad, str(exc))

    percentages = {}
    for i, item in enumerate(gegevens["percentages"]):
        pad = f"$.percentages[{i}]"
        if not isinstance(item, dict):
            _fout("ONGELDIGE_STRUCTUUR", "percentages", pad, "Percentageverdeling moet een object zijn.")
        percentage_id = _tekst(item, "percentage_id", "percentages", pad)
        if percentage_id in percentages:
            _fout("DUBBEL_PERCENTAGE_ID", "percentages", f"{pad}.percentage_id", f"Percentage-ID {percentage_id!r} komt meer dan eenmaal voor.")
        verdeling = item.get("verdeling")
        if not isinstance(verdeling, dict) or not verdeling:
            _fout("ONGELDIGE_PERCENTAGEVERDELING", "percentages", f"{pad}.verdeling", "Verdeling moet een niet-leeg object zijn.")
        genormaliseerde_verdeling = {}
        for werkstroom, percentage in verdeling.items():
            if not isinstance(werkstroom, str) or not werkstroom.strip():
                _fout("ONGELDIGE_WAARDE", "percentages", f"{pad}.verdeling", "Werkstroom-ID moet tekst zijn.")
            werkstroom_id = werkstroom.strip().lower()
            if werkstroom_id in genormaliseerde_verdeling:
                _fout("DUBBELE_WERKSTROOM", "percentages", f"{pad}.verdeling.{werkstroom}", "Werkstroom komt meerdere keren voor na normalisatie.")
            genormaliseerde_verdeling[werkstroom_id] = _getal(
                percentage, "percentages", f"{pad}.verdeling.{werkstroom}", 0, 1, positief=True
            )
        if sum(genormaliseerde_verdeling.values()) > 1:
            _fout("ONGELDIGE_PERCENTAGEVERDELING", "percentages", f"{pad}.verdeling", "De totale percentageverdeling mag niet groter zijn dan 100%.")
        try:
            percentages[percentage_id] = Percentageverdeling(percentage_id, genormaliseerde_verdeling)
        except (TypeError, ValueError) as exc:
            _fout("ONGELDIGE_PERCENTAGEVERDELING", "percentages", pad, str(exc))

    toewijzingen = []
    for i, item in enumerate(gegevens["toewijzingen"]):
        pad = f"$.toewijzingen[{i}]"
        if not isinstance(item, dict):
            _fout("ONGELDIGE_STRUCTUUR", "toewijzingen", pad, "Toewijzing moet een object zijn.")
        userid = _tekst(item, "userid", "toewijzingen", pad)
        type_ = _tekst(item, "type", "toewijzingen", pad)
        toewijzing_id = _tekst(item, "toewijzing_id", "toewijzingen", pad)
        if userid not in medewerkers_op_id:
            _fout("ONBEKENDE_MEDEWERKER", "toewijzingen", f"{pad}.userid", f"Onbekende medewerker: {userid}.")
        begin = _datum(item.get("geldig_vanaf"), "toewijzingen", f"{pad}.geldig_vanaf")
        eind = _datum(item.get("geldig_tm"), "toewijzingen", f"{pad}.geldig_tm", verplicht=False)
        if eind is not None and eind < begin:
            _fout("ONGELDIGE_PERIODE", "toewijzingen", pad, "geldig_tm ligt vóór geldig_vanaf.")
        medewerker = medewerkers_op_id[userid]
        if type_ == "Rooster":
            if toewijzing_id not in roosters:
                _fout("ONBEKEND_ROOSTER", "toewijzingen", f"{pad}.toewijzing_id", f"Onbekend rooster: {toewijzing_id}.")
            toewijzingen.append(Roostertoewijzing(medewerker, roosters[toewijzing_id], begin, eind))
        elif type_ == "Percentage":
            if toewijzing_id not in percentages:
                _fout("ONBEKENDE_PERCENTAGEVERDELING", "toewijzingen", f"{pad}.toewijzing_id", f"Onbekende percentageverdeling: {toewijzing_id}.")
            toewijzingen.append(PercentageToewijzing(medewerker, percentages[toewijzing_id], begin, eind))
        else:
            _fout("ONGELDIG_TOEWIJZINGSTYPE", "toewijzingen", f"{pad}.type", f"Onbekend toewijzingstype: {type_}.")

    afwezigheden = {}
    afwezigheid_records = []
    for i, item in enumerate(gegevens["afwezigheden"]):
        pad = f"$.afwezigheden[{i}]"
        if not isinstance(item, dict):
            _fout("ONGELDIGE_STRUCTUUR", "afwezigheden", pad, "Afwezigheid moet een object zijn.")
        userid = _tekst(item, "userid", "afwezigheden", pad)
        if userid not in medewerkers_op_id:
            _fout("ONBEKENDE_MEDEWERKER", "afwezigheden", f"{pad}.userid", f"Onbekende medewerker: {userid}.")
        datum = _datum(item.get("datum"), "afwezigheden", f"{pad}.datum")
        medewerker = medewerkers_op_id[userid]
        afwezigheden.setdefault(userid, {})
        if not (medewerker.startdatum <= datum and (medewerker.einddatum is None or datum <= medewerker.einddatum)):
            continue
        code = _tekst(item, "code", "afwezigheden", pad).upper()
        afwezigheid_records.append({"userid": userid, "datum": datum, "code": code, "gegevenspad": pad})
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
        "rollen": rollen,
        "medewerkers": medewerkers,
        "roosters": roosters,
        "percentages": percentages,
        "toewijzingen": toewijzingen,
        "afwezigheden": afwezigheden,
        "afwezigheid_records": afwezigheid_records,
        "agile_instellingen": agile_instellingen,
        "uren_per_storypoint": uren_per_storypoint,
    }
