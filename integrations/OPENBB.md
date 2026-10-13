# OpenBB optional integration (experimental)

This branch introduces an **isolated candidate-source adapter** in `integrations/openbb_adapter.py`. It does not alter the existing ETL, Cloudflare KV, website UI, or production configuration.

## Deployment contract

- Install `openbb-fred` and run `openbb-build` only in an isolated scheduled Python runner; do not attempt to import it in Cloudflare Workers.
- Validate installed OpenBB version and the `obb.fred.economy.fred_series` API before enabling. Provider availability may change.
- Test with a real FRED series (e.g. DGS10), compare value and observation date against the existing official FRED pipeline, and check access/limits.
- Keep the existing official FRED source as primary. Only promote OpenBB when verified; never replace a newer official observation with an older one.
- Do not publish `missing` as a numeric observation. Preserve prior dated observations with the existing stale handling.
- Do not infer support for Taiwan filings, ROIC, 2027 EPS or institutional flows from this adapter.
- The adapter is **not wired into the scheduled workflow** until real integration tests and a review pass. The PR-only CI checks offline behavior; the live-smoke job is deliberately skipped on pull requests. GitHub workflow_dispatch requires the workflow file on the default branch. Do not merge the entire experimental PR merely to enable manual dispatch. Run the isolated smoke script in an authorized test runner, or land a separate workflow-only PR after review.\n\nThe live smoke requires a valid `FRED_API_KEY` secret. No key is embedded in code. Do not interpret successful offline CI as a live FRED connection.

## Acceptance checklist

1. OpenBB version pinned and live endpoint confirmed.
2. Real responses validated for date, units, symbol and numerical values.
3. Missing/invalid/timeout results do not block existing ETL.
4. Official source remains first priority, no duplicate scoring.
5. Production site unchanged until review and separate deployment approval.

## Upstream dependency and failure-domain warning

OpenBB FRED and the official FRED API access the **same underlying FRED data provider**. They are not independent data sources. Passing parity verifies the alternate client integration, **not** upstream outage redundancy. A FRED outage, revoked key, quota/rate limit or provider-side error may affect both paths. Do not mark `independent_source_verified` or increase the macro confidence score because two FRED clients agree. For true source diversity, add and validate a separately operated upstream with compatible definitions, frequency, release lag, revisions and units.

OpenBB V5 standalone namespace is `obb.fred.economy.fred_series`, and the documented environment credential is `FRED_API_KEY`. Keep `openbb-fred` installed without legacy shared routers in the isolated runner. Source: https://docs.openbb.co/odp/python/quickstart/user and https://docs.openbb.co/odp/python/extensions/providers
