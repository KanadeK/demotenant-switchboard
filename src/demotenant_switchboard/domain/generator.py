from __future__ import annotations

import hashlib
import json
import random
from datetime import timedelta
from typing import Any

from faker import Faker

from demotenant_switchboard.domain.models import (
    DemoRecord,
    GeneratedDataset,
    ScenarioKind,
    ScenarioRecipe,
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def dataset_checksum_for(recipe_checksum: str, recipe_payload: dict[str, Any], records: list[dict[str, Any]]) -> str:
    unsigned = {
        "schema_version": "1",
        "project": "demotenant-switchboard",
        "recipe_checksum": recipe_checksum,
        "recipe": recipe_payload,
        "records": records,
    }
    return sha256_text(canonical_json(unsigned))


class DatasetGenerator:
    def generate(self, recipe: ScenarioRecipe) -> GeneratedDataset:
        recipe_payload = recipe.model_dump(mode="json")
        recipe_checksum = sha256_text(canonical_json(recipe_payload))
        records = self._records_for(recipe)
        record_payloads = [record.model_dump(mode="json") for record in records]
        dataset_checksum = dataset_checksum_for(recipe_checksum, recipe_payload, record_payloads)
        return GeneratedDataset(
            recipe_checksum=recipe_checksum,
            dataset_checksum=dataset_checksum,
            recipe=recipe,
            records=records,
        )

    def _records_for(self, recipe: ScenarioRecipe) -> list[DemoRecord]:
        faker = Faker()
        faker.seed_instance(recipe.data.seed)
        rng = random.Random(recipe.data.seed)
        factories = {
            ScenarioKind.ECOMMERCE: self._ecommerce_payload,
            ScenarioKind.PROJECT_MANAGEMENT: self._project_payload,
            ScenarioKind.SUPPORT_DESK: self._support_payload,
        }
        factory = factories[recipe.kind]
        statuses = {
            ScenarioKind.ECOMMERCE: ["cart", "paid", "packed", "shipped", "refunded"],
            ScenarioKind.PROJECT_MANAGEMENT: ["backlog", "planned", "active", "blocked", "done"],
            ScenarioKind.SUPPORT_DESK: ["new", "triaged", "waiting", "escalated", "resolved"],
        }[recipe.kind]

        records: list[DemoRecord] = []
        for index in range(recipe.data.records):
            persona = recipe.personas[index % len(recipe.personas)]
            event = recipe.timeline[index % len(recipe.timeline)]
            day_offset = (index * 7 + event.day) % recipe.data.timeline_days
            created = recipe.data.start_date + timedelta(days=day_offset)
            payload = factory(faker, rng, index)
            payload["timeline_event"] = event.label
            records.append(
                DemoRecord(
                    id=f"{recipe.tenant.slug}-{recipe.kind.value}-{index + 1:04d}",
                    kind=recipe.kind,
                    tenant_slug=recipe.tenant.slug,
                    owner=persona.slug,
                    title=str(payload["title"]),
                    status=statuses[(index + rng.randrange(len(statuses))) % len(statuses)],
                    amount=int(payload["amount"]),
                    created_at=created.isoformat(),
                    payload=payload,
                )
            )
        return records

    def _ecommerce_payload(self, faker: Faker, rng: random.Random, index: int) -> dict[str, Any]:
        product = faker.word().title()
        quantity = rng.randint(1, 7)
        unit_price = rng.randint(1200, 19000)
        return {
            "title": f"Order {index + 1} for {product}",
            "customer": faker.name(),
            "product": product,
            "quantity": quantity,
            "amount": quantity * unit_price,
            "currency": "USD",
        }

    def _project_payload(self, faker: Faker, rng: random.Random, index: int) -> dict[str, Any]:
        points = rng.choice([1, 2, 3, 5, 8, 13])
        return {
            "title": f"{faker.bs().capitalize()} #{index + 1}",
            "project": faker.catch_phrase(),
            "sprint": f"Sprint {1 + index // 20}",
            "story_points": points,
            "amount": points,
            "risk": rng.choice(["low", "medium", "high"]),
        }

    def _support_payload(self, faker: Faker, rng: random.Random, index: int) -> dict[str, Any]:
        minutes = rng.randint(15, 720)
        return {
            "title": f"Ticket {index + 1}: {faker.sentence(nb_words=5).rstrip('.')}",
            "account": faker.company(),
            "channel": rng.choice(["email", "chat", "phone", "portal"]),
            "priority": rng.choice(["p1", "p2", "p3", "p4"]),
            "amount": minutes,
            "sla_minutes": minutes,
        }
