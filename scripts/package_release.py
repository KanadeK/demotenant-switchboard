from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SLUG = "demotenant-switchboard"
SOURCE_DATE_EPOCH = "1784332800"
ZIP_TIMESTAMP = (2026, 7, 18, 0, 0, 0)


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
                info = zipfile.ZipInfo(path.relative_to(source).as_posix(), ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, path.read_bytes())


def verify_release_artifacts(release_dir: Path) -> None:
    wheel = next(release_dir.glob("*.whl"))
    data_pack = release_dir / f"{SLUG}-{VERSION}-ecommerce-data.zip"
    with tempfile.TemporaryDirectory(prefix="demotenant-release-") as temporary:
        temp_root = Path(temporary)
        unpacked = temp_root / "unpacked-ecommerce"
        with zipfile.ZipFile(data_pack) as archive:
            archive.extractall(unpacked)
        required = {"dataset.json", "records.csv", "personas.csv", "tenant.sqlite", "manifest.json"}
        found = {path.name for path in unpacked.iterdir() if path.is_file()}
        missing = required - found
        if missing:
            raise SystemExit(f"release data pack missing files: {sorted(missing)}")

        venv_dir = temp_root / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        python_bin = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        subprocess.run([str(python_bin), "-m", "pip", "install", str(wheel)], check=True)
        output_dir = temp_root / "generated"
        subprocess.run(
            [
                str(python_bin),
                "-m",
                "demotenant_switchboard.cli",
                "generate",
                str(ROOT / "examples" / "ecommerce.yaml"),
                "--output",
                str(output_dir),
            ],
            check=True,
        )
        subprocess.run(
            [
                str(python_bin),
                "-m",
                "demotenant_switchboard.cli",
                "validate",
                "--output",
                str(output_dir),
            ],
            check=True,
        )


def main() -> None:
    env = os.environ.copy()
    env["DEMOTENANT_SKIP_BENCHMARK_WRITE"] = "1"
    env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    subprocess.run([sys.executable, "scripts/demo.py"], cwd=ROOT, env=env, check=True)
    if (ROOT / "dist").exists():
        shutil.rmtree(ROOT / "dist")
    subprocess.run([sys.executable, "-m", "build"], cwd=ROOT, env=env, check=True)

    release_dir = ROOT / "dist-release"
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()

    for artifact in sorted((ROOT / "dist").glob("*")):
        shutil.copy2(artifact, release_dir / artifact.name)

    for scenario_dir in sorted((ROOT / "demo-output").iterdir()):
        if scenario_dir.is_dir():
            zip_directory(scenario_dir, release_dir / f"{SLUG}-{VERSION}-{scenario_dir.name}-data.zip")

    sums = []
    for artifact in sorted(release_dir.iterdir()):
        if artifact.is_file():
            sums.append(f"{sha256(artifact)}  {artifact.name}")
    (release_dir / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    verify_release_artifacts(release_dir)
    print(f"wrote {len(sums)} release artifacts to {release_dir}")


if __name__ == "__main__":
    main()
