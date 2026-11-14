
from datetime import date


class Rol:
    def __init__(
        self,
        rol_id,
        naam,
        standaardwerkstroom,
        geldig_vanaf,
        geldig_tm=None
    ):
        if not isinstance(rol_id, str) or not rol_id.strip():
            raise ValueError("Rol-ID is verplicht.")

        if not isinstance(naam, str) or not naam.strip():
            raise ValueError("Rolnaam is verplicht.")

        if standaardwerkstroom is not None:
            if not isinstance(standaardwerkstroom, str) or not standaardwerkstroom.strip():
                raise ValueError("Standaardwerkstroom moet een geldige tekst zijn.")

        if not isinstance(geldig_vanaf, date):
            raise ValueError("Geldig vanaf moet een datum zijn.")

        if geldig_tm is not None and not isinstance(geldig_tm, date):
            raise ValueError("Geldig t/m moet een datum zijn of None.")

        if geldig_tm is not None and geldig_tm < geldig_vanaf:
            raise ValueError("Geldig t/m mag niet vóór geldig vanaf liggen.")

        self.rol_id = rol_id.strip()
        self.naam = naam.strip()
        self.standaardwerkstroom = (
            standaardwerkstroom.strip()
            if standaardwerkstroom is not None
            else None
        )
        self.geldig_vanaf = geldig_vanaf
        self.geldig_tm = geldig_tm

    def geldt_op(self, datum):
        if not isinstance(datum, date):
            raise TypeError("datum moet een datum zijn.")

        return (
            self.geldig_vanaf <= datum
            and (self.geldig_tm is None or datum <= self.geldig_tm)
        )
