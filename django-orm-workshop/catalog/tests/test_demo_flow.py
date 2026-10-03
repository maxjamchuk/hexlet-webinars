import ast
import re
import shlex
from pathlib import Path

from django.core.management import call_command

from catalog.models import Character, Comic, Publisher, Review, Series
from catalog.tests.test_seed import catalog_snapshot


def test_entire_documented_demo_in_order(seeded, settings, capsys):
    """Execute the actual cheat sheet, including repr previews and script resets."""
    settings.DEBUG = True  # The documented connection.queries example needs query logging.
    baseline = catalog_snapshot()
    namespace = {model.__name__: model for model in (Publisher, Series, Comic, Character, Review)}
    demo = Path(__file__).resolve().parents[2] / "DEMO.md"
    blocks = re.findall(r"```(python|bash)\n(.*?)```", demo.read_text(encoding="utf-8"), re.S)
    for number, (language, code) in enumerate(blocks, start=1):
        if language == "python":
            # 'single' mode invokes displayhook like a REPL, evaluating QuerySet previews too.
            for statement in ast.parse(code).body:
                cell = compile(
                    ast.Interactive(body=[statement]), f"DEMO.md:block{number}", "single"
                )
                exec(cell, namespace)
        else:
            for line in code.splitlines():
                args = shlex.split(line)
                if args[:5] == ["uv", "run", "python", "manage.py", "runscript"]:
                    call_command("runscript", *args[5:])

    assert catalog_snapshot() == baseline
    assert len(namespace["queries"]) == 2
    assert [(c.series.title, c.issue_number) for c in namespace["comics"]] == [
        ("X-Men", 1),
        ("Amazing Spider-Man", 3),
        ("Amazing Spider-Man", 1),
        ("X-Men", 3),
    ]
    output = capsys.readouterr().out
    for expected in ["40 81", "40 41", "40 1", "40 2", "Queries: 2"]:
        assert expected in output
