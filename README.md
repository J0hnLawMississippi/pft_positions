# pft_positions

Public v0 specification for machine-readable position snapshots that Task Node agents can consume as shared group state.

This repository defines:
- Canonical schema for a position snapshot (`schema/position-snapshot.v0.schema.json`)
- Provenance and normalization conventions (`schema/README.md`)
- Exactly three v0 example payloads:
  - `schema/examples/delta-one.example.json`
  - `schema/examples/option.example.json`
  - `schema/examples/yield.example.json`

The v0 scope is intentionally narrow and implementation-ready so future adapter work (for example, CCXT-based exchange adapters) can plug into stable field names and semantics.

## Validate examples against schema

```bash
npm --prefix test install
npm --prefix test test
```

## Repository layout

```text
schema/
  position-snapshot.v0.schema.json
  README.md
  examples/
    delta-one.example.json
    option.example.json
    yield.example.json
src/
  README.md
test/
  package.json
  validate-examples.test.mjs
```
