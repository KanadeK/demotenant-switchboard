from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from demotenant_switchboard.services.switchboard import SwitchboardService

ROOT = Path(__file__).resolve().parents[2]


def test_generate_writes_json_csv_sqlite_tour_and_demo(tmp_path: Path) -> None:
    output = tmp_path / "ecommerce"
    result = SwitchboardService().generate(ROOT / "examples" / "ecommerce.yaml", output)

    expected = {
        "dataset.json",
        "records.csv",
        "personas.csv",
        "tenant.sqlite",
        "manifest.json",
        "playwright_tour.py",
        "TOUR_STEPS.md",
        "demo.html",
    }
    assert expected == {path.name for path in output.iterdir()}
    assert len(result.checksum) == 64

    dataset = json.loads((output / "dataset.json").read_text(encoding="utf-8"))
    assert dataset["dataset_checksum"] == result.checksum
    assert len(dataset["records"]) == 100

    connection = sqlite3.connect(output / "tenant.sqlite")
    try:
        record_count = connection.execute("select count(*) from records").fetchone()[0]
        persona_count = connection.execute("select count(*) from personas").fetchone()[0]
    finally:
        connection.close()
    assert record_count == 100
    assert persona_count == 5


def test_validate_detects_tampered_dataset(tmp_path: Path) -> None:
    output = tmp_path / "support"
    service = SwitchboardService()
    service.generate(ROOT / "examples" / "support_desk.yaml", output)
    payload = json.loads((output / "dataset.json").read_text(encoding="utf-8"))
    payload["records"][0]["status"] = "tampered"
    (output / "dataset.json").write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="dataset checksum"):
        service.validate(output)


def test_reset_restores_initial_checksum_after_file_change(tmp_path: Path) -> None:
    output = tmp_path / "projects"
    recipe = ROOT / "examples" / "project_management.yaml"
    service = SwitchboardService()
    first = service.generate(recipe, output)
    (output / "records.csv").write_text("bad,data\n", encoding="utf-8")

    second = service.reset(recipe, output)

    assert first.checksum == second.checksum
    assert service.validate(output)["checksum"] == first.checksum


def test_secret_like_output_fails_validation(tmp_path: Path) -> None:
    output = tmp_path / "ecommerce"
    service = SwitchboardService()
    service.generate(ROOT / "examples" / "ecommerce.yaml", output)
    manifest = output / "manifest.json"
    fake_token = "ghp_" + "123456789012345678901234"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace("northstar-shop", f"token='{fake_token}'"),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="secret-like"):
        service.validate(output)
