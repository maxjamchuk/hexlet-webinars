"""Запуск четырёх демонстраций и тестов текущим интерпретатором."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PREFIXES = {
    "json_parsing": [
        "valid-user.json: OK",
        "invalid-syntax.json: PARSE ERROR at line ",
    ],
    "json_schema_validation": [
        "valid-user.json: VALID",
        "invalid-user.json: INVALID",
        "  - age: expected integer",
        "  - name: must not be empty",
        "schema-valid-business-invalid.json: VALID",
    ],
    "csv_parsing": [
        "split(',') -> 4 pieces",
        "csv.reader -> 3 fields",
        "42 | Smith, John | 27",
    ],
    "data_quality": [
        "Rows: 8",
        "- row 4: missing name",
        "- row 5: age 180 is outside 0..120",
        "- row 6: duplicate id=1",
        '- row 7: name "  Maria  " -> "Maria"',
        "Valid rows: 5",
        "Invalid rows: 3",
    ],
}


def check_command(name, arguments, expected_prefixes):
    result = subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    lines = result.stdout.splitlines()
    missing = [
        prefix for prefix in expected_prefixes
        if not any(line.startswith(prefix) for line in lines)
    ]
    if result.returncode != 0 or missing:
        print(f"{name}: FAILED (exit code {result.returncode})")
        for line in missing:
            print(f"Missing stdout line prefix: {line}")
        print(f"stdout:\n{result.stdout}")
        print(f"stderr:\n{result.stderr}")
        return False
    print(f"{name}: OK")
    return True


def main():
    for name, expected_prefixes in EXPECTED_PREFIXES.items():
        if not check_command(name, ["-m", f"examples.{name}"], expected_prefixes):
            return 1
    if not check_command("pytest", ["-m", "pytest", "-q"], []):
        return 1
    print("\nSmoke check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
