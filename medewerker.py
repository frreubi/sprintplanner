from datetime import date

class Medewerker:
    ROLLEN = ("ops", "dev", "pm", "sm", "po", "func")

    def __init__(
        self,
        userid,
        voornaam,
        tussenvoegsel,
        achternaam,
        rol,
        dev=0,
        ops=0,
        func=0,
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
        self.dev = dev
        self.ops = ops
        self.func = func
        self.beheerder = beheerder
        self.access_analist = access_analist
        self.einddatum = einddatum

    @property
    def dev(self):
        return self._dev

    @dev.setter
    def dev(self, waarde):
        self._controleer_percentage(waarde, "DEV")
        self._dev = waarde

    @property
    def ops(self):
        return self._ops

    @ops.setter
    def ops(self, waarde):
        self._controleer_percentage(waarde, "OPS")
        self._ops = waarde

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, waarde):
        self._controleer_percentage(waarde, "FUNC")
        self._func = waarde

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
        if not isinstance(waarde, str) or waarde.strip().lower() not in self.ROLLEN:
            raise ValueError(
                f"Rol moet een van deze waarden zijn: {', '.join(self.ROLLEN)}."
            )
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
        totaal = medewerker.dev + medewerker.ops + medewerker.func
        if round(totaal, 2) != 100:
            waarschuwingen.append(
                f"{medewerker.naam}: rolpercentages tellen op tot {totaal:g}% in plaats van 100%."
            )
    return waarschuwingen
