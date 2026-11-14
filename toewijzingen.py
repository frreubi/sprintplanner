
from datetime import date

from medewerker import Medewerker
from rooster import Rooster
from percentages import Percentageverdeling


class Geldigheid:
    def __init__(self, geldig_vanaf: date, geldig_tm: date | None = None):
        if not isinstance(geldig_vanaf, date):
            raise TypeError("geldig_vanaf moet een datum zijn")
        if geldig_tm is not None and not isinstance(geldig_tm, date):
            raise TypeError("geldig_tm moet een datum zijn of None")
        if geldig_tm is not None and geldig_tm < geldig_vanaf:
            raise ValueError("geldig_tm mag niet vóór geldig_vanaf liggen")

        self.geldig_vanaf = geldig_vanaf
        self.geldig_tm = geldig_tm

    def geldt_op(self, datum: date) -> bool:
        if not isinstance(datum, date):
            raise TypeError("datum moet een datum zijn")

        return (
            self.geldig_vanaf <= datum
            and (self.geldig_tm is None or datum <= self.geldig_tm)
        )


class Roostertoewijzing(Geldigheid):
    def __init__(
        self,
        medewerker: Medewerker,
        rooster: Rooster,
        geldig_vanaf: date,
        geldig_tm: date | None = None,
    ):
        if not isinstance(medewerker, Medewerker):
            raise TypeError("medewerker moet een Medewerker zijn")
        if not isinstance(rooster, Rooster):
            raise TypeError("rooster moet een Rooster zijn")

        super().__init__(geldig_vanaf, geldig_tm)

        self.medewerker = medewerker
        self.rooster = rooster


class PercentageToewijzing(Geldigheid):
    def __init__(
        self,
        medewerker: Medewerker,
        percentageverdeling: Percentageverdeling,
        geldig_vanaf: date,
        geldig_tm: date | None = None,
    ):
        if not isinstance(medewerker, Medewerker):
            raise TypeError("medewerker moet een Medewerker zijn")
        if not isinstance(percentageverdeling, Percentageverdeling):
            raise TypeError("percentageverdeling moet een Percentageverdeling zijn")

        super().__init__(geldig_vanaf, geldig_tm)

        self.medewerker = medewerker
        self.percentageverdeling = percentageverdeling



def zoek_toewijzing(
    medewerker: Medewerker,
    datum: date,
    toewijzingen: list,
) -> tuple[Roostertoewijzing, PercentageToewijzing | None]:

    if not isinstance(medewerker, Medewerker):
        raise TypeError("medewerker moet een Medewerker zijn")
    if not isinstance(datum, date):
        raise TypeError("datum moet een datum zijn")

    geldig = [
        toewijzing
        for toewijzing in toewijzingen
        if toewijzing.medewerker is medewerker
        and toewijzing.geldt_op(datum)
    ]

    roosters = [
        t for t in geldig
        if isinstance(t, Roostertoewijzing)
    ]

    percentages = [
        t for t in geldig
        if isinstance(t, PercentageToewijzing)
    ]

    if len(roosters) != 1:
        if not roosters:
            omschrijving = "Geen roostertoewijzing gevonden (0 geldige roostertoewijzingen)"
        else:
            omschrijving = f"{len(roosters)} geldige roostertoewijzingen gevonden"
        raise ValueError(
            f"Medewerker {medewerker.userid} heeft op {datum}: {omschrijving}."
        )

    if len(percentages) > 1:
        raise ValueError(
            f"Medewerker {medewerker.userid} heeft op {datum} "
            f"{len(percentages)} geldige percentage-toewijzingen."
        )

    return roosters[0], percentages[0] if percentages else None
