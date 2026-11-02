from datetime import date

class Medewerker:

    def __init__(
        self,
        userid,
        voornaam,
        tussenvoegsel,
        achternaam,
        rol,
        werkstromen,    
        beheerder=False,
        access_analist=False,
        einddatum=None,
    ):
        if not isinstance(beheerder, bool):
            raise ValueError("Beheerder moet True of False zijn.")
        if not isinstance(access_analist, bool):
            raise ValueError("AccessAnalist moet True of False zijn.")
        if einddatum is not None and not isinstance(einddatum, date):
            raise ValueError("Einddatum moet een datum zijn of None.")

        self.userid = userid
        self.voornaam = voornaam
        self.tussenvoegsel = tussenvoegsel
        self.achternaam = achternaam
        self.rol = rol
        self.werkstromen = werkstromen
        self.beheerder = beheerder
        self.access_analist = access_analist
        self.einddatum = einddatum

    @property
    def werkstromen(self):
        return self._werkstromen

    @werkstromen.setter
    def werkstromen(self, waarden):
        if not isinstance(waarden, dict):
            raise ValueError("Werkstromen moeten als dictionary worden aangeleverd.")

        for naam, percentage in waarden.items():
            if not isinstance(naam, str) or not naam.strip():
                raise ValueError("Iedere werkstroom moet een geldige naam hebben.")

            self._controleer_percentage(percentage, naam.upper())

        self._werkstromen = {
            naam.strip().lower(): percentage
            for naam, percentage in waarden.items()
        }

    @staticmethod
    def _controleer_percentage(waarde, naam):
        if (
            not isinstance(waarde, (int, float))
            or isinstance(waarde, bool)
            or not 0 <= waarde <= 100
        ):
            raise ValueError(f"Percentage {naam} moet een getal van 0 t/m 100 zijn.")

    @property
    def voornaam(self):
        return self._voornaam

    @voornaam.setter
    def voornaam(self, waarde):
        if not isinstance(waarde, str) or not waarde.strip():
            raise ValueError("Voornaam is verplicht.")
        self._voornaam = waarde.strip()

    @property
    def tussenvoegsel(self):
        return self._tussenvoegsel

    @tussenvoegsel.setter
    def tussenvoegsel(self, waarde):
        if not isinstance(waarde, str):
            raise ValueError("Tussenvoegsel moet tekst zijn.")
        self._tussenvoegsel = waarde.strip()

    @property
    def achternaam(self):
        return self._achternaam

    @property
    def rol(self):
        return self._rol

    @rol.setter
    def rol(self, waarde):
        if not isinstance(waarde, str) or not waarde.strip():
            raise ValueError("Rol mag niet leeg zijn.")
        self._rol = waarde.strip().lower()

    @achternaam.setter
    def achternaam(self, waarde):
        if not isinstance(waarde, str) or not waarde.strip():
            raise ValueError("Achternaam is verplicht.")
        self._achternaam = waarde.strip()

    @property
    def userid(self):
        return self._userid

    @userid.setter
    def userid(self, waarde):
        if not isinstance(waarde, str) or not waarde.strip():
            raise ValueError("Userid is verplicht.")
        self._userid = waarde.strip()

    @property
    def naam(self):
        delen = [self.voornaam, self.tussenvoegsel, self.achternaam]
        return " ".join(deel for deel in delen if deel)

    def __str__(self):
        return f"{self.naam} (userid: {self.userid})"

def controleer_rolpercentages(medewerkers):
    waarschuwingen = []

    for medewerker in medewerkers:
        totaal = sum(medewerker.werkstromen.values())

        if round(totaal, 2) != 100:
            waarschuwingen.append(
                f"{medewerker.naam}: werkstroompercentages "
                f"tellen op tot {totaal:g}% in plaats van 100%."
            )

    return waarschuwingen
