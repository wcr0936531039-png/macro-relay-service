# OpenBB optional integration (experimental)

This branch introduces an **isolated candidate-source adapter** in `integrations/openbb_adapter.py`. It does not alter the existing ETL, Cloudflare KV, website UI, or production configuration.

## Deployment contract

- Install `openbb` only in an isolated scheduled Python runner; do not attempt to import it in Cloudflare Workers.
- Validate installed OpenBB version and the `obb.economy.fred_series` API before enabling. Provider availability may change.
- Test with a real FRED series (e.g. DGS10), compare value and observation date against the existing official FRED pipeline, and check access/limits.
- Keep the existing official FRED source as primary. Only promote OpenBB when verified; never replace a newer official observation with an older one.
- Do not publish `missing` as a numeric observation. Preserve prior dated observations with the existing stale handling.
- Do not infer support for Taiwan filings, ROIC, 2027 EPS or institutional flows from this adapter.
- The adapter is **not wired into the scheduled workflow** until real integration tests and a review pass.

## Acceptance checklist

1. OpenBB version pinned and live endpoint confirmed.
2. Real responses validated for date, units, symbol and numerical values.
3. Missing/invalid/timeout results do not block existing ETL.
4. Official source remains first priority, no duplicate scoring.
5. Production site unchanged until review and separate deployment approval.
