from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "demo-output",
    "dist",
    "dist-release",
}
ALLOWED_FILES = {
    "README.md",
    "README.zh-CN.md",
    "SECURITY.md",
    "docs/PRIVACY_AND_SECURITY.md",
    "scripts/release_check.py",
    "scripts/secret_scan.py",
}
PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_.-]{12,}", re.IGNORECASE),
]


def should_scan(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    if relative in ALLOWED_FILES:
        return False
    return not any(part in EXCLUDED_PARTS for part in path.parts)


def main() -> None:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or not should_scan(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in PATTERNS):
                findings.append(f"{path.relative_to(ROOT)}:{line_number}: {line}")
    if findings:
        raise SystemExit("secret-like value found:\n" + "\n".join(findings))
    print("secret scan passed")


if __name__ == "__main__":
    main()
