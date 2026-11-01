
class Rooster:
    DAGEN = ("maandag", "dinsdag", "woensdag", "donderdag", "vrijdag")

    def __init__(self, rooster_id, cyclus_weken, uren_per_week):
        if not isinstance(rooster_id, str) or not rooster_id.strip():
            raise ValueError("Rooster-ID is verplicht.")

        if cyclus_weken not in (1, 2):
            raise ValueError("De roostercyclus moet 1 of 2 weken zijn.")

        if len(uren_per_week) != cyclus_weken:
            raise ValueError("Het aantal weekpatronen past niet bij de cyclus.")

        for week in uren_per_week:
            if len(week) != 5:
                raise ValueError("Iedere week moet vijf werkdagen bevatten.")
            for uren in week:
                if not isinstance(uren, (int, float)) or isinstance(uren, bool):
                    raise ValueError("Roosteruren moeten getallen zijn.")
                if not 0 <= uren <= 24:
                    raise ValueError("Roosteruren moeten tussen 0 en 24 liggen.")

        self.rooster_id = rooster_id.strip()
        self.cyclus_weken = cyclus_weken
        self.uren_per_week = tuple(tuple(week) for week in uren_per_week)
        

    def uren_op(self, datum):
        dag = datum.isoweekday()
        if dag > 5:
            return 0

        weekpatroon = 0 if self.cyclus_weken == 1 else (datum.isocalendar().week + 1) % 2
        return self.uren_per_week[weekpatroon][dag - 1]
