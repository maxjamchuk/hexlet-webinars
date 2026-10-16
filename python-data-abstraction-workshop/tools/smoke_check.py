"""Быстрая проверка самостоятельных стадий воркшопа."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
STAGES = (
    "00-naive",
    "01-broken-representation",
    "02-interface-list",
    "03-interface-dict",
    "04-invariants",
    "05-key-mechanic",
    "06-bonus-sparse-world",
)


def run(stage, command):
    try:
        return subprocess.run(
            [sys.executable, *command],
            cwd=ROOT / stage,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise AssertionError(f"{stage}: timeout for {' '.join(command)}") from error


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check_stage(stage):
    demo = run(stage, ["demo.py"])
    tests = run(stage, ["-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-v"])
    require(tests.returncode == 0 and "OK" in tests.stderr,
            f"{stage}: unittest failed\n{tests.stdout}{tests.stderr}")

    if stage == "01-broken-representation":
        require(demo.returncode != 0, f"{stage}: demo should fail")
        require("An error is expected." in demo.stdout,
                f"{stage}: missing explanatory header")
        require("KeyError: 0" in demo.stderr and "get_tile" in demo.stderr,
                f"{stage}: unexpected error\n{demo.stderr}")
        print(f"PASS {stage}: expected KeyError; tests OK")
        return demo.stdout

    require(demo.returncode == 0, f"{stage}: demo failed\n{demo.stderr}")
    require("START: (1, 1)" in demo.stdout and "WIN" in demo.stdout,
            f"{stage}: missing start or victory")
    if stage.startswith(("05", "06")):
        require("KEY COLLECTED" in demo.stdout and
                "EXIT LOCKED: key required" in demo.stdout and
                "ROUTE A: without key" in demo.stdout and
                "ROUTE B: with key" in demo.stdout,
                f"{stage}: key routes incomplete")
    elif stage == "04-invariants":
        require(demo.stdout.count("EXPECTED INVALID MAP:") >= 4,
                f"{stage}: missing invalid map examples")
    else:
        require("MOVE a: blocked" in demo.stdout and "EXIT REACHED" in demo.stdout,
                f"{stage}: movement events missing")
    print(f"PASS {stage}: demo and tests OK")
    return demo.stdout


def main():
    outputs = {stage: check_stage(stage) for stage in STAGES}
    require((ROOT / STAGES[0] / "game.py").read_bytes() ==
            (ROOT / STAGES[1] / "game.py").read_bytes(),
            "00 and 01 game.py differ")
    print("PASS identical game.py: 00-naive, 01-broken-representation")
    for group in (STAGES[2:5], STAGES[5:]):
        files = [(ROOT / stage / "game.py").read_bytes() for stage in group]
        require(all(item == files[0] for item in files[1:]),
                f"game.py differs in {', '.join(group)}")
        print(f"PASS identical game.py: {', '.join(group)}")

    normal = outputs["02-interface-list"]
    require(normal == outputs["03-interface-dict"],
            "02 and 03 normal game outputs differ")
    require(normal == outputs["04-invariants"].split("EXPECTED INVALID MAP:")[0],
            "04 normal game output differs")
    require(outputs["05-key-mechanic"] == outputs["06-bonus-sparse-world"],
            "05 and 06 game outputs differ")
    print("PASS equivalent game outputs: 02-04 and 05-06")
    print("SMOKE CHECK PASSED: 7 stages")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print(f"SMOKE CHECK FAILED: {error}", file=sys.stderr)
        raise SystemExit(1) from error
