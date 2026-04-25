# Canonical Position Snapshot v0

This directory publishes the canonical v0 schema used by Task Node agents to exchange shared position state.

Scope note: v0 is position-sharing only. Trend/contrarian/churn/sentiment/strategy signal components are intentionally out of scope and may be added in a future schema version.

## Versioning

- `schema_version` is the wire-level contract version and must be `position-snapshot.v0`.
- `spec_date` for this release is fixed to `2026-04`.
- Backward-incompatible changes require a new `schema_version`.

## Provenance Rules

Every snapshot must include a top-level `provenance` object with:

- `collector`: identity and software version of the collector/publisher
- `sources`: one or more source records (API, wallet, manual, or derived)
- `content_hash`: SHA-256 of the canonical JSON payload used for integrity checks

Each source entry should include:

- `source_type`: one of `api`, `wallet`, `manual`, `derived`
- `source_id`: stable identifier such as `ccxt:binance` or `rpc:arbitrum`
- `fetched_at`: UTC timestamp of the pull
- Optional evidence references (`request_id`, `endpoint`, `tx_hash`, `cid`)

## Normalization Conventions

- Numeric values are decimal strings (no floating-point JSON numbers).
- Timestamps are RFC 3339 UTC (`date-time`).
- Currency and units are explicit per field.
- `side` uses economic direction (`long`, `short`, `neutral`).
- `valuation_ccy` is explicit and required per position.
- `notional_value`, `mark_price`, and PnL values are normalized into the snapshot's declared valuation context.
- Exchange metadata should map to CCXT conventions using `ccxt.exchange_id`, `ccxt.market_symbol`, and related IDs.
- `risk` is required per position and contains `liquidation_price` and `value_at_risk_1d`.

## Canonical Hash Rule

`provenance.content_hash` is computed by:

1. Parsing the snapshot JSON.
2. Omitting `provenance.content_hash` from the object.
3. Serializing canonical JSON with recursive object-key sorting, compact separators, preserved array order, and UTF-8 encoding.
4. Computing lowercase SHA-256 hex over those canonical bytes.

This avoids circular hashing and makes validation deterministic across whitespace and object key ordering differences.

## Instrument Coverage in v0

v0 requires support for three instrument categories:

- `delta_one`
- `option`
- `yield`

The example payloads in `schema/examples/` cover these categories and reference Binance, Hyperliquid, Deribit, and Arbitrum-based yield context.
