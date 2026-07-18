# Competitor Scan

Scan date: 2026-07-18  
Tooling: `gh auth status`, `gh api user`, and `gh search repos` through the GitHub CLI.  
Authenticated user observed before scan: `KanadeK`.

## Collision Checks

- `DemoTenant Switchboard`: no exact-name result in the sampled GitHub search.
- `demotenant-switchboard`: no exact-slug result in the sampled GitHub search.
- `KanadeK/demotenant-switchboard`: `gh repo view` could not resolve a repository with that name.

## Related Public Repositories Sampled

| Repository | Stars | Updated | Main function | Overlap | Difference |
| --- | ---: | --- | --- | --- | --- |
| boxblinkracer/shopware-ai-demodata | 29 | 2026-05-16 | AI demo data plugin for Shopware 6 | Demo data generation | Product-specific; not a generic YAML SaaS tenant switchboard. |
| openemr/demo-data-generator | 20 | 2026-07-07 | Fictional demo data for OpenEMR | Demo records | Healthcare/OpenEMR-specific; no persona switching or Playwright tour DSL. |
| analyst-collective/data-generator | 10 | 2025-10-10 | Clojure demo data generator | Demo rows | Generic data generator, not SaaS scenario/tour workflow. |
| camunda-consulting/camunda-util-demo-data-generator | 9 | 2021-11-21 | Camunda demo utilities | Demo data | Older and product-specific. |
| ff4f/seedgen | 8 | 2026-07-09 | Deterministic PostgreSQL seed generator | Deterministic seed data | Database-focused; no tenant/persona/tour artifacts. |
| openeobs/openeobs_demo_data_generator | 3 | 2025-11-18 | Open-eObs demo data generator | Demo data | Product-specific. |
| SimonOfHH/DemoDataGenerator | 3 | 2026-05-01 | Contoso-compatible Business Central data modules | Demo data | ERP-specific and live-data oriented. |
| Krusty84/TCPresaleDreamland | 3 | 2026-03-12 | Teamcenter presales demo data | Presales demo support | Teamcenter-specific; no portable YAML DSL. |
| saivineeth100/erpnext_demo_data | 2 | 2025-08-22 | ERPNext demo data | Demo data | ERPNext-specific. |
| exercism/seeds | 2 | 2023-01-28 | Exercism seed data | Seed data | Domain-specific fixture data, not SaaS demo tenant orchestration. |

## Decision

The default repository name `demotenant-switchboard` is safe to use based on this sampled scan. No active project in the sample appears to overlap the MVP by more than about 70%.

The project keeps its planned differentiation:

- YAML scenario recipes for tenant, persona, data, timeline, and story.
- Deterministic reset through dataset checksum.
- SQLite, JSON, and CSV outputs.
- Persona session generation.
- Playwright tour script and human-readable tour steps.
- Three built-in SaaS verticals.
