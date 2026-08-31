from customs import calculate_fee


def main():
    checks = [
        (10, "standard", 1000),
        (10, "fragile", 1500),
    ]

    for weight, cargo_type, expected in checks:
        actual = calculate_fee(weight, cargo_type)
        print(
            f"{cargo_type}: ожидалось {expected}, "
            f"получено {actual}"
        )


if __name__ == "__main__":
    main()
