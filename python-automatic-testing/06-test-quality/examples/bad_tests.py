from customs import calculate_fee, inspect_cargo


SHARED_MANIFEST = {
    "name": "Контейнер с картошкой",
    "weight": 10,
    "cargo_type": "standard",
    "declared": True,
}


def test_1():
    assert calculate_fee(10, "standard") == 1000


def test_without_assert():
    calculate_fee(10, "fragile")


def test_several_unrelated_rules():
    assert calculate_fee(10, "standard") == 1000
    assert calculate_fee(21, "fragile") == 3650
    assert inspect_cargo(SHARED_MANIFEST) == "accepted"


def test_changes_shared_manifest():
    SHARED_MANIFEST["declared"] = False
    assert inspect_cargo(SHARED_MANIFEST) == "rejected"


def test_uses_shared_manifest_after_change():
    assert inspect_cargo(SHARED_MANIFEST) == "accepted"
