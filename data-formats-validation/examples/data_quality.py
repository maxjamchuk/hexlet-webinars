"""CSV разобран: теперь проверяем значения и качество записей."""

import csv
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "csv" / "users-dirty.csv"


def normalize_record(record):
    normalized = record.copy()
    normalized["name"] = record["name"].strip()
    return normalized


def validate_record(record):
    problems = []
    if not record["name"]:
        problems.append("missing name")
    try:
        age = int(record["age"])
    except ValueError:
        problems.append("age must be an integer")
    else:
        if not 0 <= age <= 120:
            problems.append(f"age {age} is outside 0..120")
    if record["active"] not in ("true", "false"):
        problems.append("active must be true or false")
    return problems


def analyze_rows(rows):
    report = {"rows": 0, "valid": 0, "invalid": 0, "problems": [], "normalizations": []}
    seen_ids = set()
    for line_number, original in rows:
        record = normalize_record(original)
        report["rows"] += 1
        if record["name"] != original["name"]:
            report["normalizations"].append(
                f'row {line_number}: name "{original["name"]}" -> "{record["name"]}"'
            )
        problems = validate_record(record)
        if record["id"] in seen_ids:
            problems.append(f'duplicate id={record["id"]}')
        seen_ids.add(record["id"])
        for problem in problems:
            report["problems"].append(f"row {line_number}: {problem}")
        if problems:
            report["invalid"] += 1
        else:
            report["valid"] += 1
    return report


def read_rows():
    with DATA_FILE.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        return [(reader.line_num, record) for record in reader]


def main():
    report = analyze_rows(read_rows())
    print(f'Rows: {report["rows"]}')
    print("\nProblems:")
    for problem in report["problems"]:
        print(f"- {problem}")
    print("\nNormalizations:")
    for normalization in report["normalizations"]:
        print(f"- {normalization}")
    print(f'\nValid rows: {report["valid"]}')
    print(f'Invalid rows: {report["invalid"]}')


if __name__ == "__main__":
    main()
