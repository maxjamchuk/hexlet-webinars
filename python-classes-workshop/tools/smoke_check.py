"""Run each stage in its own process to isolate identically named modules."""

import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE_NAME = re.compile(r"0[0-8]-[a-z-]+$")


def run(command, directory):
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, *command],
        cwd=directory,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        check=False,
    )


def main():
    stages = sorted(path for path in ROOT.iterdir()
                    if path.is_dir() and STAGE_NAME.fullmatch(path.name))
    expected = {f"{number:02d}" for number in range(9)}
    found = {path.name[:2] for path in stages}
    if found != expected or len(stages) != 9:
        print(f"Wrong stage set: found {sorted(found)}, expected {sorted(expected)}")
        return 1

    passed = failed = 0
    for stage in stages:
        demo = run(["demo.py"], stage)
        tests = run(["-m", "unittest", "discover", "-p", "test_models.py", "-v"], stage)
        count = re.search(r"Ran (\d+) tests?", tests.stderr)
        test_count = count.group(1) if count else "?"
        okay = (demo.returncode == tests.returncode == 0
                and count is not None and int(test_count) > 0)
        print(f"{stage.name}: {'OK' if okay else 'FAIL'} "
              f"(demo={demo.returncode}, tests={tests.returncode}, cases={test_count})")
        if okay:
            passed += 1
        else:
            failed += 1
            if tests.returncode == 0 and test_count in ("?", "0"):
                print(f"--- {stage.name}: no tests discovered ---")
            for label, result in (("demo", demo), ("tests", tests)):
                if result.returncode:
                    print(f"--- {stage.name}/{label} stdout ---\n{result.stdout}")
                    print(f"--- {stage.name}/{label} stderr ---\n{result.stderr}")

    print(f"Total: {passed} passed, {failed} failed stages.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
