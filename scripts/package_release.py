from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SLUG = "demotenant-switchboard"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def zip_directory(source: Path, target: Path) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source))


def main() -> None:
    subprocess.run([sys.executable, "scripts/demo.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "-m", "build"], cwd=ROOT, check=True)

    release_dir = ROOT / "dist-release"
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()

    for artifact in sorted((ROOT / "dist").glob("*")):
        shutil.copy2(artifact, release_dir / f"{SLUG}-{VERSION}-{artifact.name}")

    for scenario_dir in sorted((ROOT / "demo-output").iterdir()):
        if scenario_dir.is_dir():
            zip_directory(scenario_dir, release_dir / f"{SLUG}-{VERSION}-{scenario_dir.name}-data.zip")

    sums = []
    for artifact in sorted(release_dir.iterdir()):
        if artifact.is_file():
            sums.append(f"{sha256(artifact)}  {artifact.name}")
    (release_dir / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(f"wrote {len(sums)} release artifacts to {release_dir}")


if __name__ == "__main__":
    main()
