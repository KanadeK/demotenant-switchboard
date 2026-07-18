from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from demotenant_switchboard.adapters.files import load_recipe
from demotenant_switchboard.domain.generator import DatasetGenerator
from demotenant_switchboard.domain.models import ScenarioRecipe

ROOT = Path(__file__).resolve().parents[2]


def test_generation_is_deterministic_for_same_seed() -> None:
    recipe = load_recipe(ROOT / "examples" / "ecommerce.yaml")
    first = DatasetGenerator().generate(recipe)
    second = DatasetGenerator().generate(recipe)

    assert first.dataset_checksum == second.dataset_checksum
    assert [record.model_dump(mode="json") for record in first.records] == [
        record.model_dump(mode="json") for record in second.records
    ]


def test_each_builtin_recipe_has_required_personas_records_and_tour() -> None:
    for recipe_path in (ROOT / "examples").glob("*.yaml"):
        recipe = load_recipe(recipe_path)
        dataset = DatasetGenerator().generate(recipe)

        assert len(recipe.personas) >= 5
        assert len(recipe.tour) >= 8
        assert len(dataset.records) >= 100
        assert all(record.tenant_slug == recipe.tenant.slug for record in dataset.records)


def test_invalid_tour_actor_is_rejected() -> None:
    payload = {
        "schema_version": "1",
        "kind": "ecommerce",
        "tenant": {"slug": "demo-shop", "name": "Demo Shop", "plan": "team", "region": "us"},
        "personas": [
            {"slug": f"user-{index}", "name": f"User {index}", "role": "Role", "permissions": ["read"]}
            for index in range(5)
        ],
        "data": {"records": 1, "seed": 1, "start_date": "2026-01-01"},
        "timeline": [{"day": 0, "label": "Start", "impact": "Demo starts"}],
        "tour": [
            {
                "title": f"Step {index}",
                "actor": "missing-user",
                "route": "/",
                "selector": "[data-testid='record-count']",
                "assertion": "records",
            }
            for index in range(8)
        ],
    }

    with pytest.raises(ValidationError, match="not defined personas"):
        ScenarioRecipe.model_validate(payload)
