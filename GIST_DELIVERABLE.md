# PFT Position Snapshot v0 - Public Deliverable

Canonical position-sharing specification for Task Node and downstream agents.

Full schema source: `https://raw.githubusercontent.com/J0hnLawMississippi/pft_positions/main/schema/position-snapshot.v0.schema.json`

Scope note: v0 is position sharing only. Trend/contrarian/churn/sentiment/strategy signal components are intentionally excluded from the schema and examples, and can be integrated in a future schema version.

## 1) Canonical Snapshot Field Table

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | yes | Must be `position-snapshot.v0` |
| `spec_date` | string | yes | Must be `2026-04` |
| `snapshot_id` | string | yes | Unique ID for snapshot instance |
| `as_of` | RFC3339 datetime | yes | Position state timestamp |
| `published_at` | RFC3339 datetime | yes | Publish timestamp |
| `prev_snapshot_ref` | string | no | Optional previous snapshot pointer |
| `publisher` | object | yes | Publisher identity, optional signature material |
| `group_context` | object | yes | Scope and valuation context |
| `provenance` | object | yes | Collector metadata, source evidence, content hash |
| `normalization` | object | yes | Numeric/time/sign conventions |
| `positions` | array | yes | One or more normalized positions |

Position object (core):
- `position_id`, `instrument_type`, `asset_class`, `venue`, `account_ref`
- `side`, `quantity`, `unit`, `valuation_ccy`
- `mark_price`, `notional_value`, `cost_basis`, `pnl_unrealized`, `pnl_realized`
- `risk` (includes `liquidation_price`, `value_at_risk_1d`)
- optional instrument blocks:
  - `delta_one`
  - `option`
  - `yield`
- optional CCXT mapping block:
  - `ccxt.exchange_id`, `ccxt.market_symbol`, `ccxt.market_id`, `ccxt.base`, `ccxt.quote`, `ccxt.settle`

## 2) Provenance and Normalization Rules

### Provenance
- Every snapshot includes a top-level `provenance` object.
- `provenance.collector` identifies collector ID and software version.
- `provenance.sources` includes one or more source records, each with:
  - `source_type`: `api | wallet | manual | derived`
  - `source_id`: stable source identifier (for example `ccxt:binance`, `ccxt:deribit`, `rpc:arbitrum`)
  - `fetched_at`: RFC3339 UTC timestamp
  - optional evidence refs (`request_id`, `endpoint`, `tx_hash`, `cid`)
- `provenance.content_hash` is SHA-256 (hex) of canonical payload bytes.

### Normalization
- Numeric values are decimal strings.
- Timestamps are RFC3339 UTC date-time.
- `side` is explicit (`long`, `short`, `neutral`) with positive `quantity`.
- `valuation_ccy` is explicit per position.
- PnL uses `profit-positive` / `loss-negative` convention.
- Exchange/market IDs follow CCXT conventions where applicable.

## 3) Example Payloads (Exactly Three)

### A) Delta-One Example (Binance + Hyperliquid)

```json
{
  "schema_version": "position-snapshot.v0",
  "spec_date": "2026-04",
  "snapshot_id": "snap_delta1_2026-04-24T100000Z",
  "as_of": "2026-04-24T10:00:00Z",
  "published_at": "2026-04-24T10:00:04Z",
  "publisher": {
    "entity_id": "tasknode-group-alpha-engine",
    "entity_type": "group_bot"
  },
  "group_context": {
    "group_id": "network-alpha-cohort-a",
    "snapshot_scope": "network",
    "valuation_ccy": "USD"
  },
  "provenance": {
    "collector": {
      "id": "pft-positions-collector",
      "version": "0.1.0"
    },
    "sources": [
      {
        "source_type": "api",
        "source_id": "ccxt:binance",
        "fetched_at": "2026-04-24T10:00:01Z",
        "endpoint": "fapiPrivateGetPositionRisk"
      },
      {
        "source_type": "api",
        "source_id": "ccxt:hyperliquid",
        "fetched_at": "2026-04-24T10:00:02Z",
        "endpoint": "privatePostInfo"
      }
    ],
    "content_hash": "b9e81aa92180c160f232722414f56a98d44331b803c9abed63521a9c4ddab6eb"
  },
  "normalization": {
    "numeric_encoding": "decimal-string",
    "timestamp_encoding": "rfc3339-utc",
    "pnl_sign_convention": "profit-positive",
    "quantity_sign_convention": "side-and-positive-quantity"
  },
  "positions": [
    {
      "position_id": "binance-btcusdt-perp-main",
      "instrument_type": "delta_one",
      "asset_class": "crypto",
      "venue": {
        "venue_id": "binance",
        "venue_type": "cex"
      },
      "account_ref": "acct:binance:subaccount-main",
      "ccxt": {
        "exchange_id": "binance",
        "market_symbol": "BTC/USDT:USDT",
        "market_id": "BTCUSDT",
        "base": "BTC",
        "quote": "USDT",
        "settle": "USDT"
      },
      "side": "long",
      "quantity": "2.2500",
      "unit": "BTC",
      "valuation_ccy": "USD",
      "mark_price": "72150.5",
      "notional_value": "162338.63",
      "cost_basis": "154920.00",
      "pnl_unrealized": "7418.63",
      "pnl_realized": "1200.15",
      "risk": {
        "liquidation_price": "58640.2",
        "value_at_risk_1d": "8421.25"
      },
      "delta_one": {
        "symbol": "BTCUSDT",
        "contract_kind": "perpetual",
        "entry_price": "68853.3",
        "leverage": "3"
      }
    },
    {
      "position_id": "hyperliquid-solusd-perp-alpha",
      "instrument_type": "delta_one",
      "asset_class": "crypto",
      "venue": {
        "venue_id": "hyperliquid",
        "venue_type": "dex"
      },
      "account_ref": "acct:hyperliquid:agent-14",
      "ccxt": {
        "exchange_id": "hyperliquid",
        "market_symbol": "SOL/USD:USD",
        "market_id": "SOL-PERP",
        "base": "SOL",
        "quote": "USD",
        "settle": "USD"
      },
      "side": "short",
      "quantity": "1800",
      "unit": "SOL",
      "valuation_ccy": "USD",
      "mark_price": "173.42",
      "notional_value": "312156.00",
      "cost_basis": "326880.00",
      "pnl_unrealized": "14724.00",
      "pnl_realized": "-850.00",
      "risk": {
        "liquidation_price": "241.10",
        "value_at_risk_1d": "19210.00"
      },
      "delta_one": {
        "symbol": "SOL-PERP",
        "contract_kind": "perpetual",
        "entry_price": "181.60",
        "leverage": "4"
      }
    }
  ]
}
```

### B) Option Example (Deribit)

```json
{
  "schema_version": "position-snapshot.v0",
  "spec_date": "2026-04",
  "snapshot_id": "snap_option_2026-04-24T100500Z",
  "as_of": "2026-04-24T10:05:00Z",
  "published_at": "2026-04-24T10:05:03Z",
  "publisher": {
    "entity_id": "tasknode-options-engine",
    "entity_type": "service"
  },
  "group_context": {
    "group_id": "network-volatility-desk",
    "snapshot_scope": "network",
    "valuation_ccy": "USD"
  },
  "provenance": {
    "collector": {
      "id": "pft-positions-collector",
      "version": "0.1.0"
    },
    "sources": [
      {
        "source_type": "api",
        "source_id": "ccxt:deribit",
        "fetched_at": "2026-04-24T10:05:01Z",
        "endpoint": "private/get_positions"
      }
    ],
    "content_hash": "53202dda93a8c398bdcc8fb575c9928f4b7f30ccd86115ca61ba0b720fc44517"
  },
  "normalization": {
    "numeric_encoding": "decimal-string",
    "timestamp_encoding": "rfc3339-utc",
    "pnl_sign_convention": "profit-positive",
    "quantity_sign_convention": "side-and-positive-quantity"
  },
  "positions": [
    {
      "position_id": "deribit-btc-20260626-80000-c",
      "instrument_type": "option",
      "asset_class": "crypto",
      "venue": {
        "venue_id": "deribit",
        "venue_type": "cex"
      },
      "account_ref": "acct:deribit:vol-book-1",
      "ccxt": {
        "exchange_id": "deribit",
        "market_symbol": "BTC/USD:BTC-260626-80000-C",
        "market_id": "BTC-26JUN26-80000-C",
        "base": "BTC",
        "quote": "USD",
        "settle": "BTC"
      },
      "side": "long",
      "quantity": "35",
      "unit": "contracts",
      "valuation_ccy": "USD",
      "mark_price": "4380.00",
      "notional_value": "153300.00",
      "cost_basis": "132650.00",
      "pnl_unrealized": "20650.00",
      "pnl_realized": "-1220.00",
      "risk": {
        "liquidation_price": "0.00",
        "value_at_risk_1d": "9870.00"
      },
      "option": {
        "underlying": "BTC",
        "option_type": "call",
        "strike": "80000",
        "expiry": "2026-06-26T08:00:00Z",
        "style": "european",
        "multiplier": "1",
        "implied_volatility": "0.56",
        "greeks": {
          "delta": "0.43",
          "gamma": "0.00011",
          "vega": "0.18",
          "theta": "-0.021"
        }
      }
    }
  ]
}
```

### C) Yield Example (Binance Staking + Arbitrum USD.ai)

```json
{
  "schema_version": "position-snapshot.v0",
  "spec_date": "2026-04",
  "snapshot_id": "snap_yield_2026-04-24T101000Z",
  "as_of": "2026-04-24T10:10:00Z",
  "published_at": "2026-04-24T10:10:05Z",
  "publisher": {
    "entity_id": "tasknode-yield-monitor",
    "entity_type": "tasknode_agent"
  },
  "group_context": {
    "group_id": "network-yield-cohort",
    "snapshot_scope": "cohort",
    "valuation_ccy": "USD"
  },
  "provenance": {
    "collector": {
      "id": "pft-positions-collector",
      "version": "0.1.0"
    },
    "sources": [
      {
        "source_type": "api",
        "source_id": "ccxt:binance",
        "fetched_at": "2026-04-24T10:10:01Z",
        "endpoint": "sapi/v1/simple-earn/flexible/position"
      },
      {
        "source_type": "wallet",
        "source_id": "rpc:arbitrum",
        "fetched_at": "2026-04-24T10:10:02Z"
      },
      {
        "source_type": "derived",
        "source_id": "protocol:usd-ai",
        "fetched_at": "2026-04-24T10:10:03Z"
      }
    ],
    "content_hash": "6a8ccc332602436844e2b7b1eba6d1c8ab223e51e36c67570c64a66767820939"
  },
  "normalization": {
    "numeric_encoding": "decimal-string",
    "timestamp_encoding": "rfc3339-utc",
    "pnl_sign_convention": "profit-positive",
    "quantity_sign_convention": "side-and-positive-quantity"
  },
  "positions": [
    {
      "position_id": "binance-staking-bnb-flex",
      "instrument_type": "yield",
      "asset_class": "crypto",
      "venue": {
        "venue_id": "binance",
        "venue_type": "cex"
      },
      "account_ref": "acct:binance:earn-main",
      "ccxt": {
        "exchange_id": "binance",
        "base": "BNB"
      },
      "side": "long",
      "quantity": "850.00",
      "unit": "BNB",
      "valuation_ccy": "USD",
      "mark_price": "598.20",
      "notional_value": "508470.00",
      "cost_basis": "471750.00",
      "pnl_unrealized": "36720.00",
      "pnl_realized": "8200.00",
      "risk": {
        "liquidation_price": "0.00",
        "value_at_risk_1d": "15240.00"
      },
      "yield": {
        "protocol": "binance-simple-earn",
        "position_kind": "staking",
        "principal": "850.00",
        "reward_assets": [
          "BNB"
        ],
        "apr": "0.041",
        "apy": "0.042",
        "lockup": {
          "is_locked": false
        }
      }
    },
    {
      "position_id": "arbitrum-usdai-vault-main",
      "instrument_type": "yield",
      "asset_class": "rate",
      "venue": {
        "venue_id": "usd-ai",
        "venue_type": "onchain_protocol",
        "chain_id": 42161,
        "network": "arbitrum"
      },
      "account_ref": "0x2d4b8d7d55aef49c9c347e1546623e5f9f8a6102",
      "side": "long",
      "quantity": "220000.00",
      "unit": "USDAI",
      "valuation_ccy": "USD",
      "mark_price": "1.0000",
      "notional_value": "220000.00",
      "cost_basis": "214800.00",
      "pnl_unrealized": "5200.00",
      "pnl_realized": "0.00",
      "risk": {
        "liquidation_price": "0.00",
        "value_at_risk_1d": "3100.00"
      },
      "yield": {
        "protocol": "usd-ai",
        "position_kind": "vault",
        "principal": "220000.00",
        "reward_assets": [
          "USDAI",
          "ARB"
        ],
        "apr": "0.098",
        "apy": "0.103",
        "lockup": {
          "is_locked": true,
          "unlock_at": "2026-07-24T00:00:00Z"
        }
      }
    }
  ]
}
```

## 4) Handoff: How Task Node / Agents Consume This

1. Ingestion adapters (CCXT + on-chain) collect raw positions.
2. Normalization layer transforms raw data into this schema.
3. Consumers validate `schema_version` and verify `provenance.content_hash`.
4. Agents read `positions` as shared state for portfolio-awareness and task coordination.
5. Execution and analytics modules can then map normalized positions to venue-specific actions.
