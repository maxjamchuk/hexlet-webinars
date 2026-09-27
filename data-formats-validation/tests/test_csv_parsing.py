import csv

from examples import csv_parsing as demo


def test_naive_split_breaks_quoted_name():
    pieces = demo.read_first_data_line().split(",")
    assert pieces == ["42", '"Smith', ' John"', "27"]
    assert len(pieces) == 4


def test_csv_reader_preserves_name():
    fields = next(csv.reader([demo.read_first_data_line()]))
    assert len(fields) == 3
    assert fields == ["42", "Smith, John", "27"]


def test_demo_output(capsys):
    demo.main()
    assert capsys.readouterr().out == (
        'Input:\n42,"Smith, John",27\n\n'
        "split(',') -> 4 pieces\n"
        '42 | "Smith |  John" | 27\n\n'
        "csv.reader -> 3 fields\n"
        "42 | Smith, John | 27\n"
    )
