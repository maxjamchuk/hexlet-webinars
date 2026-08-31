import pytest

from customs import calculate_fee


@pytest.mark.parametrize(
    ("cargo_type", "expected_fee"),
    [
        ("standard", 1000),
        ("fragile", 1500),
        ("hazardous", 3000),
    ],
)
def test_calculate_fee_uses_cargo_rate(
    cargo_type,
    expected_fee,
):
    assert calculate_fee(10, cargo_type) == expected_fee


@pytest.mark.parametrize(
    ("weight", "expected_fee"),
    [
        (19, 1900),
        (20, 2000),
        (21, 2600),
    ],
)
def test_calculate_fee_around_overweight_limit(
    weight,
    expected_fee,
):
    assert calculate_fee(weight, "standard") == expected_fee


def test_calculate_fee_rejects_negative_weight():
    with pytest.raises(
        ValueError,
        match="Weight must be greater than zero",
    ):
        calculate_fee(-1, "standard")


def test_calculate_fee_rejects_unknown_cargo_type():
    with pytest.raises(
        ValueError,
        match="Unknown cargo type",
    ):
        calculate_fee(10, "livestock")
