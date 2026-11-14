
from datetime import date

import pytest

from medewerker import Medewerker
from rooster import Rooster
from percentages import Percentageverdeling
from toewijzingen import (
    Roostertoewijzing,
    PercentageToewijzing,
    zoek_toewijzing,
)


def maak_medewerker():
    return Medewerker(
        userid="j001",
        voornaam="Jan",
        tussenvoegsel="",
        achternaam="Jansen",
        rol="OPS",
    )


def maak_rooster():
    return Rooster("R001", 1, [[8, 8, 8, 8, 8]])


def maak_percentageverdeling():
    return Percentageverdeling("P001", {"DEV": 0.10})


def test_roostertoewijzing_aanmaken():
    medewerker = maak_medewerker()
    rooster = maak_rooster()

    toewijzing = Roostertoewijzing(
        medewerker, rooster, date(2025, 1, 1)
    )

    assert toewijzing.medewerker is medewerker
    assert toewijzing.rooster is rooster
    assert toewijzing.geldig_tm is None


def test_percentagetoewijzing_aanmaken():
    medewerker = maak_medewerker()
    verdeling = maak_percentageverdeling()

    toewijzing = PercentageToewijzing(
        medewerker, verdeling, date(2025, 1, 1)
    )

    assert toewijzing.medewerker is medewerker
    assert toewijzing.percentageverdeling is verdeling


def test_ongeldige_medewerker():
    with pytest.raises(TypeError):
        Roostertoewijzing(
            "j001", maak_rooster(), date(2025, 1, 1)
        )


def test_ongeldig_rooster():
    with pytest.raises(TypeError):
        Roostertoewijzing(
            maak_medewerker(), "R001", date(2025, 1, 1)
        )


def test_ongeldige_percentageverdeling():
    with pytest.raises(TypeError):
        PercentageToewijzing(
            maak_medewerker(), "P001", date(2025, 1, 1)
        )


def test_ongeldige_geldigheidsperiode():
    with pytest.raises(ValueError):
        Roostertoewijzing(
            maak_medewerker(),
            maak_rooster(),
            date(2025, 2, 1),
            date(2025, 1, 1),
        )


def test_geldt_op():
    toewijzing = Roostertoewijzing(
        maak_medewerker(),
        maak_rooster(),
        date(2025, 1, 1),
        date(2025, 12, 31),
    )

    assert toewijzing.geldt_op(date(2025, 1, 1))
    assert toewijzing.geldt_op(date(2025, 12, 31))
    assert not toewijzing.geldt_op(date(2026, 1, 1))


def test_zoek_toewijzing_zonder_percentage():
    medewerker = maak_medewerker()
    rooster = Roostertoewijzing(
        medewerker, maak_rooster(), date(2025, 1, 1)
    )

    gevonden_rooster, gevonden_percentage = zoek_toewijzing(
        medewerker, date(2025, 6, 1), [rooster]
    )

    assert gevonden_rooster is rooster
    assert gevonden_percentage is None


def test_zoek_toewijzing_met_percentage():
    medewerker = maak_medewerker()
    rooster = Roostertoewijzing(
        medewerker, maak_rooster(), date(2025, 1, 1)
    )
    percentage = PercentageToewijzing(
        medewerker, maak_percentageverdeling(), date(2025, 1, 1)
    )

    gevonden_rooster, gevonden_percentage = zoek_toewijzing(
        medewerker, date(2025, 6, 1), [rooster, percentage]
    )

    assert gevonden_rooster is rooster
    assert gevonden_percentage is percentage


def test_zoek_toewijzing_zonder_rooster():
    medewerker = maak_medewerker()

    with pytest.raises(ValueError, match="roostertoewijzingen"):
        zoek_toewijzing(medewerker, date(2025, 6, 1), [])


def test_zoek_toewijzing_met_meerdere_percentages():
    medewerker = maak_medewerker()
    rooster = Roostertoewijzing(
        medewerker, maak_rooster(), date(2025, 1, 1)
    )
    percentages = [
        PercentageToewijzing(
            medewerker, maak_percentageverdeling(), date(2025, 1, 1)
        )
        for _ in range(2)
    ]

    with pytest.raises(ValueError, match="percentage-toewijzingen"):
        zoek_toewijzing(
            medewerker,
            date(2025, 6, 1),
            [rooster, *percentages],
        )
