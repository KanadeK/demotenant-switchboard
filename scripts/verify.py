from __future__ import annotations

import subprocess
import sys

COMMANDS = [
    [sys.executable, "-m", "ruff", "check", "."],
    [sys.executable, "-m", "mypy", "src"],
    [sys.executable, "scripts/secret_scan.py"],
    [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
    ],
    [sys.executable, "-m", "build"],
]


def main() -> None:
    for command in COMMANDS:
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
