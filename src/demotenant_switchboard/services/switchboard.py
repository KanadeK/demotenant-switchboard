from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from demotenant_switchboard.adapters.files import (
    load_recipe,
    read_json,
    write_dataset_files,
    write_json,
)
from demotenant_switchboard.adapters.sqlite import table_count, write_sqlite
from demotenant_switchboard.domain.generator import (
    DatasetGenerator,
    canonical_json,
    dataset_checksum_for,
    sha256_text,
)
from demotenant_switchboard.domain.models import GeneratedDataset

SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_.-]{12,}"),
]


@dataclass(frozen=True)
class GenerationResult:
    output_dir: Path
    checksum: str
    files: dict[str, str]


class SwitchboardService:
    def __init__(self) -> None:
        self._generator = DatasetGenerator()
        self._templates = Environment(
            loader=PackageLoader("demotenant_switchboard", "templates"),
            autoescape=select_autoescape(disabled_extensions=("j2",)),
            keep_trailing_newline=True,
        )

    def generate(self, recipe_path: Path, output_dir: Path) -> GenerationResult:
        recipe = load_recipe(recipe_path)
        dataset = self._generator.generate(recipe)
        files = write_dataset_files(dataset, output_dir)
        sqlite_path = output_dir / "tenant.sqlite"
        write_sqlite(dataset, sqlite_path)
        files["sqlite"] = str(sqlite_path)
        self.export_tour(output_dir)
        self.export_demo_app(output_dir)
        return GenerationResult(output_dir=output_dir, checksum=dataset.dataset_checksum, files=files)

    def reset(self, recipe_path: Path, output_dir: Path) -> GenerationResult:
        return self.generate(recipe_path, output_dir)

    def validate(self, output_dir: Path) -> dict[str, object]:
        dataset_path = output_dir / "dataset.json"
        manifest_path = output_dir / "manifest.json"
        sqlite_path = output_dir / "tenant.sqlite"
        if not dataset_path.exists() or not manifest_path.exists() or not sqlite_path.exists():
            raise ValueError("output directory is missing dataset.json, manifest.json, or tenant.sqlite")

        dataset = GeneratedDataset.model_validate(read_json(dataset_path))
        manifest = read_json(manifest_path)
        recipe_payload = dataset.recipe.model_dump(mode="json")
        record_payloads = [record.model_dump(mode="json") for record in dataset.records]
        recomputed_recipe_checksum = sha256_text(canonical_json(recipe_payload))
        recomputed_dataset_checksum = dataset_checksum_for(
            recomputed_recipe_checksum,
            recipe_payload,
            record_payloads,
        )
        if dataset.recipe_checksum != recomputed_recipe_checksum:
            raise ValueError("stored recipe checksum does not match recipe content")
        if dataset.dataset_checksum != recomputed_dataset_checksum:
            raise ValueError("stored dataset checksum does not match dataset content")
        if manifest["dataset_checksum"] != dataset.dataset_checksum:
            raise ValueError("manifest checksum does not match dataset checksum")
        if table_count(sqlite_path, "records") != len(dataset.records):
            raise ValueError("SQLite record count does not match dataset.json")
        if self._contains_secret(dataset_path) or self._contains_secret(manifest_path):
            raise ValueError("generated output appears to contain a secret-like value")

        return {
            "scenario": dataset.recipe.kind.value,
            "tenant": dataset.recipe.tenant.slug,
            "records": len(dataset.records),
            "personas": len(dataset.recipe.personas),
            "checksum": dataset.dataset_checksum,
            "valid": True,
        }

    def switch_persona(self, output_dir: Path, persona_slug: str) -> dict[str, object]:
        dataset = GeneratedDataset.model_validate(read_json(output_dir / "dataset.json"))
        persona = next((item for item in dataset.recipe.personas if item.slug == persona_slug), None)
        if persona is None:
            known = ", ".join(item.slug for item in dataset.recipe.personas)
            raise ValueError(f"unknown persona '{persona_slug}'. Known personas: {known}")
        visible_records = [record.id for record in dataset.records if record.owner == persona.slug]
        session = {
            "tenant": dataset.recipe.tenant.slug,
            "persona": persona.model_dump(mode="json"),
            "visible_record_ids": visible_records,
            "visible_record_count": len(visible_records),
            "dataset_checksum": dataset.dataset_checksum,
        }
        write_json(output_dir / "session.json", session)
        return session

    def export_tour(self, output_dir: Path) -> dict[str, str]:
        dataset = GeneratedDataset.model_validate(read_json(output_dir / "dataset.json"))
        context = {"dataset": dataset, "tour": dataset.recipe.tour}
        script_path = output_dir / "playwright_tour.py"
        steps_path = output_dir / "TOUR_STEPS.md"
        script_path.write_text(self._templates.get_template("playwright_tour.py.j2").render(context), encoding="utf-8")
        steps_path.write_text(self._templates.get_template("tour_steps.md.j2").render(context), encoding="utf-8")
        return {"script": str(script_path), "steps": str(steps_path)}

    def export_demo_app(self, output_dir: Path) -> Path:
        dataset = GeneratedDataset.model_validate(read_json(output_dir / "dataset.json"))
        html_path = output_dir / "demo.html"
        html_path.write_text(
            self._templates.get_template("demo.html.j2").render({"dataset": dataset}),
            encoding="utf-8",
        )
        return html_path

    def _contains_secret(self, path: Path) -> bool:
        text = path.read_text(encoding="utf-8")
        return any(pattern.search(text) for pattern in SECRET_PATTERNS)
