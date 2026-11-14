from datetime import date

class Medewerker:

    def __init__(
        self,
        userid,
        voornaam,
        tussenvoegsel,
        achternaam,
        rol,
        beheerder=False,
        access_analist=False,
        einddatum=None,
        startdatum=date(2025, 1, 1),
    ):
        if not isinstance(beheerder, bool):
            raise ValueError("Beheerder moet True of False zijn.")
        if not isinstance(access_analist, bool):
            raise ValueError("AccessAnalist moet True of False zijn.")
        if not isinstance(startdatum, date):
            raise ValueError("Startdatum moet een datum zijn.")
        if einddatum is not None and not isinstance(einddatum, date):
            raise ValueError("Einddatum moet een datum zijn of None.")
        if einddatum is not None and einddatum < startdatum:
            raise ValueError("Einddatum mag niet vóór de startdatum liggen.")

        self.userid = userid
        self.voornaam = voornaam
        self.tussenvoegsel = tussenvoegsel
        self.achternaam = achternaam
        self.rol = rol
        self.beheerder = beheerder
        self.access_analist = access_analist
        self.startdatum = startdatum
        self.einddatum = einddatum

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

