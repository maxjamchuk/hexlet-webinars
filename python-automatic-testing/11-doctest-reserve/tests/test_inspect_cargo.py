import pytest

from customs import inspect_cargo


@pytest.fixture
def standard_manifest():
    return {
        "name": "Контейнер с картошкой",
        "weight": 10,
        "cargo_type": "standard",
        "declared": True,
    }


def test_undeclared_cargo_is_rejected(standard_manifest):
    standard_manifest["declared"] = False

    assert inspect_cargo(standard_manifest) == "rejected"


def test_standard_cargo_is_accepted(standard_manifest):
    assert inspect_cargo(standard_manifest) == "accepted"


def test_cargo_above_weight_limit_is_rejected(standard_manifest):
    standard_manifest["weight"] = 51

    assert inspect_cargo(standard_manifest) == "rejected"

def test_alien_sample_is_sent_to_quarantine(
    standard_manifest,
):
    standard_manifest["name"] = (
        "Яйца неизвестной формы жизни"
    )
    standard_manifest["cargo_type"] = "alien_sample"

    assert inspect_cargo(standard_manifest) == "quarantine"

