from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from demotenant_switchboard.cli import app

ROOT = Path(__file__).resolve().parents[2]
runner = CliRunner()


def test_cli_generates_validates_switches_and_exports_tour(tmp_path: Path) -> None:
    output = tmp_path / "ecommerce"

    generated = runner.invoke(app, ["generate", str(ROOT / "examples" / "ecommerce.yaml"), "--output", str(output)])
    assert generated.exit_code == 0, generated.output
    checksum = json.loads(generated.output)["checksum"]

    validated = runner.invoke(app, ["validate", "--output", str(output)])
    assert validated.exit_code == 0, validated.output
    assert json.loads(validated.output)["checksum"] == checksum

    switched = runner.invoke(app, ["switch", "mina-ops", "--output", str(output)])
    assert switched.exit_code == 0, switched.output
    session = json.loads(switched.output)
    assert session["persona"]["slug"] == "mina-ops"
    assert session["visible_record_count"] == 20

    tour = runner.invoke(app, ["tour", "--output", str(output)])
    assert tour.exit_code == 0, tour.output
    script_path = Path(json.loads(tour.output)["script"])
    script = script_path.read_text(encoding="utf-8")
    assert "from playwright.sync_api import expect, sync_playwright" in script
    assert "[data-testid='record-count']" in script


def test_cli_rejects_missing_recipe(tmp_path: Path) -> None:
    result = runner.invoke(app, ["generate", str(tmp_path / "missing.yaml"), "--output", str(tmp_path / "out")])

    assert result.exit_code == 2
    assert "recipe file does not exist" in result.output
