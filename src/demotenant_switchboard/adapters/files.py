from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import yaml

from demotenant_switchboard.domain.models import GeneratedDataset, ScenarioRecipe


def load_recipe(path: Path) -> ScenarioRecipe:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"recipe file does not exist: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"recipe file is not valid YAML: {path}") from exc
    if not isinstance(raw, dict):
        raise ValueError("recipe YAML must contain a mapping at the root")
    return ScenarioRecipe.model_validate(raw)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON file must contain an object at the root: {path}")
    return payload


def write_dataset_files(dataset: GeneratedDataset, output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_json = output_dir / "dataset.json"
    records_csv = output_dir / "records.csv"
    personas_csv = output_dir / "personas.csv"
    manifest = output_dir / "manifest.json"

    write_json(dataset_json, dataset.model_dump(mode="json"))
    with records_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "kind", "tenant_slug", "owner", "title", "status", "amount", "created_at"],
        )
        writer.writeheader()
        for record in dataset.records:
            writer.writerow(
                {
                    "id": record.id,
                    "kind": record.kind.value,
                    "tenant_slug": record.tenant_slug,
                    "owner": record.owner,
                    "title": record.title,
                    "status": record.status,
                    "amount": record.amount,
                    "created_at": record.created_at,
                }
            )

    with personas_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["slug", "name", "role", "permissions"])
        writer.writeheader()
        for persona in dataset.recipe.personas:
            writer.writerow(
                {
                    "slug": persona.slug,
                    "name": persona.name,
                    "role": persona.role,
                    "permissions": ";".join(persona.permissions),
                }
            )

    write_json(
        manifest,
        {
            "project": "demotenant-switchboard",
            "version": "0.1.0",
            "scenario": dataset.recipe.kind.value,
            "tenant": dataset.recipe.tenant.slug,
            "record_count": len(dataset.records),
            "persona_count": len(dataset.recipe.personas),
            "recipe_checksum": dataset.recipe_checksum,
            "dataset_checksum": dataset.dataset_checksum,
            "files": ["dataset.json", "records.csv", "personas.csv", "tenant.sqlite"],
        },
    )
    return {
        "dataset_json": str(dataset_json),
        "records_csv": str(records_csv),
        "personas_csv": str(personas_csv),
        "manifest": str(manifest),
    }
