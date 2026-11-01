from datetime import date
from medewerker import Medewerker
from rooster import Rooster

class Roostertoewijzing:
    def __init__(self, medewerker: Medewerker, rooster: Rooster,
                 geldig_vanaf: date, geldig_tm: date | None = None):
        if not isinstance(medewerker, Medewerker):
            raise TypeError("medewerker moet een Medewerker zijn")
        if not isinstance(rooster, Rooster):
            raise TypeError("rooster moet een Rooster zijn")
        if not isinstance(geldig_vanaf, date):
            raise TypeError("geldig_vanaf moet een datum zijn")
        if geldig_tm is not None and not isinstance(geldig_tm, date):
            raise TypeError("geldig_tm moet een datum zijn of None")
        if geldig_tm is not None and geldig_tm < geldig_vanaf:
            raise ValueError("geldig_tm mag niet vóór geldig_vanaf liggen")

        self.medewerker = medewerker
        self.rooster = rooster
        self.geldig_vanaf = geldig_vanaf
        self.geldig_tm = geldig_tm

    def geldt_op(self, datum: date) -> bool:
        if not isinstance(datum, date):
            raise TypeError("datum moet een datum zijn")
        return (
            self.geldig_vanaf <= datum
            and (self.geldig_tm is None or datum <= self.geldig_tm)
        )

def zoek_toewijzing(medewerker: Medewerker, datum: date,
                    toewijzingen: list[Roostertoewijzing]) -> Roostertoewijzing:
    if not isinstance(medewerker, Medewerker):
        raise TypeError("medewerker moet een Medewerker zijn")
    if not isinstance(datum, date):
        raise TypeError("datum moet een datum zijn")

    gevonden = [
        toewijzing for toewijzing in toewijzingen
        if toewijzing.medewerker is medewerker
        and toewijzing.geldt_op(datum)
    ]

    if not gevonden:
        raise ValueError(
            f"Geen roostertoewijzing gevonden voor {medewerker.userid} op {datum}"
        )
    if len(gevonden) > 1:
        raise ValueError(
            f"Meerdere roostertoewijzingen gevonden voor {medewerker.userid} op {datum}"
        )
    return gevonden[0]    