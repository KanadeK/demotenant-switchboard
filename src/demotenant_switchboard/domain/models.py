from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ScenarioKind(StrEnum):
    ECOMMERCE = "ecommerce"
    PROJECT_MANAGEMENT = "project_management"
    SUPPORT_DESK = "support_desk"


class TenantSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str = Field(min_length=3, pattern=r"^[a-z0-9][a-z0-9-]+[a-z0-9]$")
    name: str = Field(min_length=3)
    plan: str = Field(min_length=2)
    region: str = Field(min_length=2)


class PersonaSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str = Field(min_length=2, pattern=r"^[a-z0-9][a-z0-9-]+[a-z0-9]$")
    name: str = Field(min_length=2)
    role: str = Field(min_length=2)
    permissions: list[str] = Field(min_length=1)


class DataSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    records: int = Field(ge=1)
    seed: int = Field(ge=0)
    start_date: date
    timeline_days: int = Field(default=30, ge=1, le=730)


class TimelineEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: int = Field(ge=0)
    label: str = Field(min_length=3)
    impact: str = Field(min_length=3)


class TourStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=3)
    actor: str = Field(min_length=2)
    route: str = Field(pattern=r"^/")
    selector: str = Field(min_length=1)
    assertion: str = Field(min_length=3)


class ScenarioRecipe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1"] = "1"
    kind: ScenarioKind
    tenant: TenantSpec
    personas: list[PersonaSpec] = Field(min_length=5)
    data: DataSpec
    timeline: list[TimelineEvent] = Field(min_length=1)
    tour: list[TourStep] = Field(min_length=8)

    @field_validator("personas")
    @classmethod
    def persona_slugs_are_unique(cls, personas: list[PersonaSpec]) -> list[PersonaSpec]:
        slugs = [persona.slug for persona in personas]
        if len(slugs) != len(set(slugs)):
            raise ValueError("persona slugs must be unique")
        return personas

    @model_validator(mode="after")
    def tour_actors_exist(self) -> ScenarioRecipe:
        known = {persona.slug for persona in self.personas}
        missing = sorted({step.actor for step in self.tour} - known)
        if missing:
            raise ValueError(f"tour actor(s) are not defined personas: {', '.join(missing)}")
        return self


class DemoRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: ScenarioKind
    tenant_slug: str
    owner: str
    title: str
    status: str
    amount: int
    created_at: str
    payload: dict[str, Any]


class GeneratedDataset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1"] = "1"
    project: Literal["demotenant-switchboard"] = "demotenant-switchboard"
    recipe_checksum: str
    dataset_checksum: str
    recipe: ScenarioRecipe
    records: list[DemoRecord]
