from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from demotenant_switchboard.domain.models import GeneratedDataset

SCHEMA = """
create table if not exists tenants (
  slug text primary key,
  name text not null,
  plan text not null,
  region text not null
);
create table if not exists personas (
  slug text primary key,
  name text not null,
  role text not null,
  permissions_json text not null
);
create table if not exists records (
  id text primary key,
  kind text not null,
  tenant_slug text not null,
  owner text not null,
  title text not null,
  status text not null,
  amount integer not null,
  created_at text not null,
  payload_json text not null
);
"""


def write_sqlite(dataset: GeneratedDataset, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    try:
        connection.executescript(SCHEMA)
        tenant = dataset.recipe.tenant
        connection.execute(
            "insert into tenants(slug, name, plan, region) values (?, ?, ?, ?)",
            (tenant.slug, tenant.name, tenant.plan, tenant.region),
        )
        connection.executemany(
            "insert into personas(slug, name, role, permissions_json) values (?, ?, ?, ?)",
            [
                (persona.slug, persona.name, persona.role, json.dumps(persona.permissions, sort_keys=True))
                for persona in dataset.recipe.personas
            ],
        )
        connection.executemany(
            """
            insert into records(id, kind, tenant_slug, owner, title, status, amount, created_at, payload_json)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    record.id,
                    record.kind.value,
                    record.tenant_slug,
                    record.owner,
                    record.title,
                    record.status,
                    record.amount,
                    record.created_at,
                    json.dumps(record.payload, ensure_ascii=False, sort_keys=True),
                )
                for record in dataset.records
            ],
        )
        connection.commit()
    finally:
        connection.close()


def table_count(path: Path, table: str) -> int:
    if table not in {"tenants", "personas", "records"}:
        raise ValueError(f"unsupported table: {table}")
    connection = sqlite3.connect(path)
    try:
        row = connection.execute(f"select count(*) from {table}").fetchone()
    finally:
        connection.close()
    if row is None:
        raise ValueError(f"table count query returned no rows for {table}")
    return int(row[0])
