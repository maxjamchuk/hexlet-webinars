import pytest

from customs import calculate_fee


def test_calculate_fee_for_standard_cargo():
    assert calculate_fee(10, "standard") == 1000


def test_calculate_fee_for_fragile_cargo():
    assert calculate_fee(10, "fragile") == 1500


def test_calculate_fee_at_overweight_limit():
    assert calculate_fee(20, "standard") == 2000


def test_calculate_fee_above_overweight_limit():
    assert calculate_fee(21, "standard") == 2600


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
