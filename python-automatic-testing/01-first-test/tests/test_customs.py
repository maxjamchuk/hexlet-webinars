from customs import calculate_fee


def test_calculate_fee_for_standard_cargo():
    result = calculate_fee(10, "standard")

    assert result == 1000
