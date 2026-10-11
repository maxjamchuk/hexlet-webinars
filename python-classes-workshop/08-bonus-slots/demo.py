from models import PlainTrack, SlottedTrack


def main():
    plain = PlainTrack("The Cure", "A Forest", 1980)
    slotted = SlottedTrack("The Cure", "A Forest", 1980)

    print("--- Обычный экземпляр ---")
    print("plain.__dict__:", plain.__dict__)
    plain.note = "post-punk"
    print("После plain.note = ...:", plain.__dict__)

    print("\n--- __slots__ ---")
    print("SlottedTrack.__slots__:", SlottedTrack.__slots__)
    print("slotted.title:", slotted.title)
    try:
        print(slotted.__dict__)
    except AttributeError as error:
        print(f"AttributeError: {error}. У этого экземпляра нет обычного __dict__.")
    try:
        slotted.note = "post-punk"
    except AttributeError as error:
        print(f"AttributeError: {error}. Новый атрибут не объявлен в __slots__.")
    slotted.year = 1981
    print("После slotted.year = 1981:", slotted.year)
    print("__slots__ не делает объект неизменяемым.")
    print("Для многих экземпляров он может экономить память.")


if __name__ == "__main__":
    main()
