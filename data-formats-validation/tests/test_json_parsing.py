import json

import pytest

from examples import json_parsing as demo


def test_valid_json():
    user = demo.read_json(demo.DATA_DIR / "valid-user.json")
    assert user == {
        "id": 42, "name": "Anna", "email": "anna@example.com", "age": 27, "active": True
    }


def test_invalid_syntax():
    with pytest.raises(json.JSONDecodeError) as error:
        demo.read_json(demo.DATA_DIR / "invalid-syntax.json")
    assert error.value.lineno > 0
    assert error.value.colno > 0


def test_demo_classifies_both_files(capsys):
    with pytest.raises(json.JSONDecodeError) as error:
        demo.read_json(demo.DATA_DIR / "invalid-syntax.json")
    demo.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "valid-user.json: OK\n"
        f"invalid-syntax.json: PARSE ERROR at line {error.value.lineno}, "
        f"column {error.value.colno}\n"
    )
    assert captured.err == ""


def test_missing_fixture_is_not_hidden(tmp_path):
    with pytest.raises(FileNotFoundError):
        demo.read_json(tmp_path / "missing.json")


def test_data_path_does_not_depend_on_working_directory(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    demo.main()
    assert "valid-user.json: OK" in capsys.readouterr().out
