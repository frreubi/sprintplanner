
from datetime import date

import pytest

from rollen import Rol


def test_rol_aanmaken():
    rol = Rol(
        "OPS",
        "Operations",
        "OPS",
        date(2025, 1, 1)
    )

    assert rol.rol_id == "OPS"
    assert rol.naam == "Operations"
    assert rol.standaardwerkstroom == "OPS"
    assert rol.geldig_tm is None


def test_rol_zonder_standaardwerkstroom():
    rol = Rol(
        "PM",
        "Projectmanager",
        None,
        date(2025, 1, 1)
    )

    assert rol.standaardwerkstroom is None


def test_ongeldige_rol_id():
    with pytest.raises(ValueError):
        Rol("", "Operations", "OPS", date(2025, 1, 1))


def test_ongeldige_rolnaam():
    with pytest.raises(ValueError):
        Rol("OPS", "", "OPS", date(2025, 1, 1))


def test_ongeldige_geldig_vanaf():
    with pytest.raises(ValueError):
        Rol("OPS", "Operations", "OPS", "01-01-2025")


def test_geldig_tm_voor_geldig_vanaf():
    with pytest.raises(ValueError):
        Rol(
            "OPS",
            "Operations",
            "OPS",
            date(2025, 1, 2),
            date(2025, 1, 1)
        )


def test_rol_geldigheid():
    rol = Rol(
        "OPS",
        "Operations",
        "OPS",
        date(2025, 1, 1),
        date(2025, 12, 31)
    )

    assert not rol.geldt_op(date(2024, 12, 31))
    assert rol.geldt_op(date(2025, 1, 1))
    assert rol.geldt_op(date(2025, 12, 31))
    assert not rol.geldt_op(date(2026, 1, 1))
