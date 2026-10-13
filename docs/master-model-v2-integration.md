# Master Model V2 integration contract (proposal)

This repository is the macro snapshot relay, **not** the main ChatGPT Sites application. This change does not deploy or alter the existing site.

## Integration boundaries

- Keep the existing macro snapshot schema (schema_version=1, uppercase indicator IDs, ok/stale/missing).
- Preserve observed date, source, last_success, last_attempt, and stale reason. Never turn missing values into zero or PASS.
- The site must consume the macro snapshot separately from stock-specific fundamentals and AI research.
- S1 institutional/ETF flow, S2 turnover share/price efficiency, S3 trend, S4 revenue/earnings momentum, S5 macro risk are **candidate-screening** outputs. They do not replace the 10D or override hard VETO.
- Deduplicate signals: do not score a raw factor both in screening and the 10D.
- Report readiness is per module: complete, partial, pending, unavailable. Missing evidence cannot produce a final PASS.
- Fetch/validate/persist independently of interactive site requests; use cached validated data if upstream fails, explicitly labeled stale.
- Keep read tokens server-side; never ship them in client JavaScript.

## Proposed site-facing status contract

```json
{
  "schema_version": 2,
  "ticker": "8299",
  "as_of": null,
  "status": "partial",
  "modules": {
    "screening": {"status": "pending", "evidence": []},
    "fundamentals": {"status": "pending", "evidence": []},
    "macro": {"status": "pending", "evidence": []},
    "research": {"status": "pending", "evidence": []},
    "valuation": {"status": "pending", "evidence": []},
    "veto": {"status": "unknown", "evidence": []}
  },
  "final_rating": null
}
```

This is a **proposed new site contract**, not a replacement for the relay's existing schema_version=1 API.

## Acceptance tests before any production integration

1. Upstream outage returns prior observation with stale=true and original observation date.
2. No source evidence results in missing/unknown, never a fabricated score.
3. Stock-specific data is isolated by ticker and reporting period.
4. Partial report renders even if AI research times out.
5. Hard VETO is independent of screening rank; unknown VETO blocks confirmed buy rating.
6. Site deployment must be tested separately; passing relay tests does not prove site integration.
