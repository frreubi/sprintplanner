
import pytest

from percentages import Percentageverdeling


def test_percentageverdeling_aanmaken():
    verdeling = Percentageverdeling("P001", {
        "DEV": 0.50,
        "FUNC": 0.20
    })

    assert verdeling.percentage_id == "P001"
    assert verdeling.verdeling == {"DEV": 0.50, "FUNC": 0.20}


def test_enkele_werkstroom():
    verdeling = Percentageverdeling("P002", {"DEV": 0.10})

    assert verdeling.verdeling == {"DEV": 0.10}


def test_ongeldige_percentage_id():
    with pytest.raises(ValueError):
        Percentageverdeling("", {"DEV": 0.50})


def test_lege_verdeling():
    with pytest.raises(ValueError):
        Percentageverdeling("P001", {})


def test_ongeldige_werkstroom():
    with pytest.raises(ValueError):
        Percentageverdeling("P001", {"": 0.50})


@pytest.mark.parametrize("percentage", [0, -0.1, 1.1, True, "0.5"])
def test_ongeldig_percentage(percentage):
    with pytest.raises(ValueError):
        Percentageverdeling("P001", {"DEV": percentage})


def test_verdeling_meer_dan_100_procent():
    with pytest.raises(ValueError):
        Percentageverdeling("P001", {
            "DEV": 0.60,
            "FUNC": 0.50
        })
