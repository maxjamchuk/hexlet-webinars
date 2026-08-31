import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

STAGES = [
    (
        "00-manual-checks",
        [["uv", "run", "python", "manual_check.py"]],
        0,
        ["fragile: ожидалось 1500, получено 1000"],
    ),
    ("01-first-test", [["uv", "run", "pytest"]], 0, ["1 passed"]),
    (
        "02-failing-test",
        [["uv", "run", "pytest", "-v"]],
        1,
        ["1 failed", "1 passed"],
    ),
    ("03-test-scenarios", [["uv", "run", "pytest"]], 0, ["6 passed"]),
    ("04-parametrize", [["uv", "run", "pytest"]], 0, ["8 passed"]),
    ("05-fixtures", [["uv", "run", "pytest"]], 0, ["11 passed"]),
    ("06-test-quality", [["uv", "run", "pytest"]], 0, ["11 passed"]),
    (
        "07-coverage",
        [
            [
                "uv",
                "run",
                "pytest",
                "--cov=customs",
                "--cov-report=term-missing",
            ]
        ],
        0,
        ["12 passed", "TOTAL", "100%"],
    ),
    (
        "08-tdd-red",
        [["uv", "run", "pytest", "-v"]],
        1,
        ["1 failed", "12 passed"],
    ),
    ("09-tdd-green", [["uv", "run", "pytest"]], 0, ["13 passed"]),
    ("10-tdd-refactor", [["uv", "run", "pytest"]], 0, ["13 passed"]),
    (
        "11-doctest-reserve",
        [
            ["uv", "run", "pytest"],
            ["uv", "run", "python", "-m", "doctest", "-v", "customs.py"],
        ],
        0,
        ["13 passed", "2 passed.", "Test passed."],
    ),
]


def run(command, cwd):
    return subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )


def main():
    if shutil.which("uv") is None:
        print("[ERROR] uv was not found. Install uv and add it to PATH.")
        return 2

    all_ok = True

    for stage_name, commands, expected_code, fragments in STAGES:
        stage_dir = ROOT / stage_name
        sync_result = run(["uv", "sync", "--locked"], stage_dir)

        if sync_result.returncode != 0:
            print(f"[FAIL] {stage_name}: uv sync --locked failed")
            print(sync_result.stdout)
            all_ok = False
            continue

        outputs = []
        actual_codes = []
        started_at = time.perf_counter()

        for command in commands:
            result = run(command, stage_dir)
            outputs.append(result.stdout)
            actual_codes.append(result.returncode)

        elapsed = time.perf_counter() - started_at
        combined_output = "\n".join(outputs)
        codes_ok = all(code == expected_code for code in actual_codes)
        fragments_ok = all(fragment in combined_output for fragment in fragments)

        if codes_ok and fragments_ok:
            if expected_code == 1:
                detail = "expected exit code 1"
            elif stage_name == "00-manual-checks":
                detail = "exit code 0; incorrect fragile result detected"
            elif stage_name == "11-doctest-reserve":
                detail = "13 passed; 2 doctest examples passed"
            else:
                detail = ", ".join(fragments)
            print(f"[OK] {stage_name}: {detail} ({elapsed:.2f}s)")
            continue

        all_ok = False
        missing = [
            fragment for fragment in fragments if fragment not in combined_output
        ]
        print(
            f"[FAIL] {stage_name}: exit codes {actual_codes}, "
            f"expected {expected_code}"
        )
        if missing:
            print(f"  Missing output fragments: {', '.join(missing)}")
        print(combined_output)

    if all_ok:
        print("All stages behave as expected.")
        return 0

    print("Some stages did not behave as expected.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
