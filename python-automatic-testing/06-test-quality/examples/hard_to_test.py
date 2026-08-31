def ask_and_calculate_fee():
    weight = int(input("Weight: "))
    cargo_type = input("Cargo type: ")

    rates = {
        "standard": 100,
        "fragile": 150,
        "hazardous": 300,
    }
    fee = weight * rates[cargo_type]

    print(f"Fee: {fee}")
