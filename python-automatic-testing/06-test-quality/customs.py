RATES = {
    "standard": 100,
    "fragile": 150,
    "hazardous": 300,
}

OVERWEIGHT_LIMIT = 20
OVERWEIGHT_SURCHARGE = 500
MAX_ALLOWED_WEIGHT = 50


def calculate_fee(weight, cargo_type):
    if weight <= 0:
        raise ValueError("Weight must be greater than zero")

    if cargo_type not in RATES:
        raise ValueError(f"Unknown cargo type: {cargo_type}")

    fee = weight * RATES[cargo_type]

    if weight > OVERWEIGHT_LIMIT:
        fee += OVERWEIGHT_SURCHARGE

    return fee


def inspect_cargo(manifest):
    if not manifest["declared"]:
        return "rejected"

    if manifest["weight"] > MAX_ALLOWED_WEIGHT:
        return "rejected"

    return "accepted"
