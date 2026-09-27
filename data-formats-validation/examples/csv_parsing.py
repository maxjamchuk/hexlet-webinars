"""Запятая внутри кавычек — часть значения, а не разделитель полей."""

import csv
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "csv" / "users-with-comma.csv"


def read_first_data_line():
    with DATA_FILE.open(encoding="utf-8", newline="") as source:
        next(source)  # Пропускаем заголовок.
        return next(source).rstrip("\r\n")


def main():
    line = read_first_data_line()
    pieces = line.split(",")
    fields = next(csv.reader([line]))

    print(f"Input:\n{line}\n")
    print(f"split(',') -> {len(pieces)} pieces")
    print(" | ".join(pieces))
    print(f"\ncsv.reader -> {len(fields)} fields")
    print(" | ".join(fields))


if __name__ == "__main__":
    main()
