from copy import deepcopy

import pytest

from examples import data_quality as demo


@pytest.fixture
def report():
    return demo.analyze_rows(demo.read_rows())


def test_missing_name(report):
    assert "row 4: missing name" in report["problems"]


def test_age_outside_business_range(report):
    assert "row 5: age 180 is outside 0..120" in report["problems"]


def test_only_second_occurrence_is_duplicate(report):
    duplicates = [problem for problem in report["problems"] if "duplicate" in problem]
    assert duplicates == ["row 6: duplicate id=1"]


def test_maria_normalization(report):
    maria = demo.read_rows()[5][1]
    assert demo.normalize_record(maria)["name"] == "Maria"
    assert report["normalizations"] == ['row 7: name "  Maria  " -> "Maria"']


def test_report_totals(report):
    assert (report["rows"], report["valid"], report["invalid"]) == (8, 5, 3)
    assert len(report["problems"]) == 3


def test_original_records_and_csv_are_not_modified():
    rows = demo.read_rows()
    original_rows = deepcopy(rows)
    original_file = demo.DATA_FILE.read_bytes()
    demo.analyze_rows(rows)
    assert rows == original_rows
    assert demo.DATA_FILE.read_bytes() == original_file


@pytest.mark.parametrize("age", ["0", "120"])
def test_age_boundaries_are_valid(age):
    record = demo.read_rows()[0][1]
    record["age"] = age
    assert demo.validate_record(record) == []


@pytest.mark.parametrize("age", ["-1", "121", "27.5", "unknown", ""])
def test_invalid_age(age):
    record = demo.read_rows()[0][1]
    record["age"] = age
    assert len(demo.validate_record(record)) == 1


@pytest.mark.parametrize("active", ["True", "yes", "1", "", " true "])
def test_active_has_no_implicit_conversion(active):
    record = demo.read_rows()[0][1]
    record["active"] = active
    assert demo.validate_record(record) == ["active must be true or false"]


def test_whitespace_name_is_missing_after_normalization():
    record = demo.read_rows()[0][1]
    record["name"] = "   "
    assert demo.validate_record(demo.normalize_record(record)) == ["missing name"]


def test_multiple_problems_count_as_one_invalid_row():
    record = demo.read_rows()[0][1]
    record.update(name="", age="180", active="yes")
    report = demo.analyze_rows([(2, record)])
    assert len(report["problems"]) == 3
    assert (report["rows"], report["valid"], report["invalid"]) == (1, 0, 1)


def test_demo_output(capsys):
    demo.main()
    assert capsys.readouterr().out == (
        "Rows: 8\n\n"
        "Problems:\n"
        "- row 4: missing name\n"
        "- row 5: age 180 is outside 0..120\n"
        "- row 6: duplicate id=1\n\n"
        "Normalizations:\n"
        '- row 7: name "  Maria  " -> "Maria"\n\n'
        "Valid rows: 5\n"
        "Invalid rows: 3\n"
    )
