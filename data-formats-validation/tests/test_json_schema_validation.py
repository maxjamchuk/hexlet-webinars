import json

import pytest
from jsonschema import Draft202012Validator

from examples import json_schema_validation as demo


@pytest.fixture
def validator():
    schema = json.loads(demo.SCHEMA_FILE.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def load_user(filename):
    return json.loads((demo.DATA_DIR / filename).read_text(encoding="utf-8"))


def test_valid_user(validator):
    assert demo.validation_errors(validator, load_user("valid-user.json")) == []


def test_both_schema_errors_are_reported_in_field_order(validator):
    user = load_user("invalid-user.json")
    errors = list(validator.iter_errors(user))
    assert {(tuple(error.path), error.validator) for error in errors} == {
        (("age",), "type"), (("name",), "minLength")
    }
    assert demo.validation_errors(validator, user) == [
        "age: expected integer", "name: must not be empty"
    ]


def test_error_order_does_not_depend_on_property_order(validator):
    user = load_user("invalid-user.json")
    reversed_user = dict(reversed(list(user.items())))
    assert demo.validation_errors(validator, reversed_user) == [
        "age: expected integer", "name: must not be empty"
    ]


def test_business_invalid_user_passes_schema(validator):
    user = load_user("schema-valid-business-invalid.json")
    assert user["age"] == 250
    assert demo.validation_errors(validator, user) == []


@pytest.mark.parametrize("field", ["id", "name", "email", "age", "active"])
def test_all_fields_are_required(validator, field):
    user = load_user("valid-user.json")
    del user[field]
    assert not validator.is_valid(user)


def test_demo_output(capsys):
    demo.main()
    assert capsys.readouterr().out == (
        "valid-user.json: VALID\n\n"
        "invalid-user.json: INVALID\n"
        "  - age: expected integer\n"
        "  - name: must not be empty\n\n"
        "schema-valid-business-invalid.json: VALID\n\n"
    )
