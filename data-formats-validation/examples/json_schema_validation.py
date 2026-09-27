"""Синтаксис JSON, соответствие схеме и бизнес-правила — разные проверки."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "json"
SCHEMA_FILE = ROOT / "schemas" / "user.schema.json"


def main():
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    filenames = (
        "valid-user.json",
        "invalid-user.json",
        "schema-valid-business-invalid.json",
    )
    for filename in filenames:
        user = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
        errors = validation_errors(validator, user)
        status = "INVALID" if errors else "VALID"
        print(f"{filename}: {status}")
        for error in errors:
            print(f"  - {error}")
        print()


def validation_errors(validator, user):
    errors = sorted(
        validator.iter_errors(user),
        key=lambda error: tuple(str(part) for part in error.path),
    )
    return [format_error(error) for error in errors]


def format_error(error):
    field = ".".join(str(part) for part in error.path) or "object"
    if error.validator == "type":
        message = f"expected {error.validator_value}"
    elif error.validator == "minLength" and error.validator_value == 1:
        message = "must not be empty"
    else:
        message = error.message
    return f"{field}: {message}"


if __name__ == "__main__":
    main()
