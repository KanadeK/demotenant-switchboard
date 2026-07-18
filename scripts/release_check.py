from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
AUTHOR = "KanadeK <121669563+KanadeK@users.noreply.github.com>"


def run(command: list[str]) -> str:
    return subprocess.check_output(command, cwd=ROOT, text=True, encoding="utf-8").strip()


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    assert_true(f'__version__ = "{VERSION}"' in (ROOT / "src" / "demotenant_switchboard" / "__init__.py").read_text(encoding="utf-8"), "package version mismatch")
    assert_true(f"## v{VERSION}" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), "CHANGELOG missing release")
    release_dir = ROOT / "dist-release"
    assert_true(release_dir.exists(), "dist-release does not exist; run package first")
    assert_true((release_dir / "SHA256SUMS.txt").exists(), "SHA256SUMS.txt missing")
    artifacts = [path for path in release_dir.iterdir() if path.is_file()]
    assert_true(len(artifacts) >= 6, "expected wheel, sdist, data packs, and checksums")

    status = run(["git", "status", "--short"])
    assert_true(status == "", f"working tree is not clean:\n{status}")

    author_lines = run(["git", "log", "--format=%an <%ae> | %cn <%ce>"])
    for line in author_lines.splitlines():
        assert_true(line == f"{AUTHOR} | {AUTHOR}", f"unexpected author/committer: {line}")

    banned_markers = ["TO" + "DO", "FIX" + "ME", "Not" + "Implemented", "place" + "holder", "coming" + " soon", "lorem" + " ipsum"]
    marker_scan = subprocess.run(
        ["git", "grep", "-nE", "|".join(banned_markers)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    allowed = [line for line in marker_scan.stdout.splitlines() if "docs/ROADMAP.md" in line]
    unexpected = [line for line in marker_scan.stdout.splitlines() if line not in allowed]
    assert_true(not unexpected, "empty-shell marker found:\n" + "\n".join(unexpected))

    subprocess.run([sys.executable, "scripts/secret_scan.py"], cwd=ROOT, check=True)
    print("release check passed")


if __name__ == "__main__":
    main()
