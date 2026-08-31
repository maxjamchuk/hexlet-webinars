from customs import inspect_cargo


def test_hazardous_cargo_is_sent_to_quarantine():
    manifest = {
        "name": "Радиоактивный тостер",
        "weight": 8,
        "cargo_type": "hazardous",
        "declared": True,
    }

    assert inspect_cargo(manifest) == "quarantine"

