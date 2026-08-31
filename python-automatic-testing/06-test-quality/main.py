from customs import calculate_fee


def main():
    weight = int(input("Weight: "))
    cargo_type = input("Cargo type: ")
    fee = calculate_fee(weight, cargo_type)
    print(f"Fee: {fee}")


if __name__ == "__main__":
    main()
