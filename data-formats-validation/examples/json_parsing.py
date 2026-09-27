"""Parsing проверяет синтаксис JSON, но не смысл данных."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    for filename in ("valid-user.json", "invalid-syntax.json"):
        try:
            read_json(DATA_DIR / filename)
        except json.JSONDecodeError as error:
            print(
                f"{filename}: PARSE ERROR "
                f"at line {error.lineno}, column {error.colno}"
            )
        else:
            print(f"{filename}: OK")


if __name__ == "__main__":
    main()
