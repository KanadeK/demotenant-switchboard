# Privacy And Security

DemoTenant Switchboard is offline-first. It does not call external APIs during generation, validation, reset, persona switching, or tour export.

## Safe Inputs

- Synthetic tenant names
- Synthetic personas
- Seed values
- Demo timeline labels
- Local-only selectors and routes

## Unsafe Inputs

- API keys, tokens, cookies, passwords, or private certificates
- Real customer exports
- Production support tickets
- Private account names or employee records
- Proprietary screenshots or third-party copyrighted assets

## Validation

`demotenant-switchboard validate` checks generated JSON and manifest files for common token-like patterns. This is a guardrail, not a substitute for human review.

## Generated Data

Built-in examples use Faker with fixed seeds. Re-running the same recipe with the same dependency versions produces the same checksum.
