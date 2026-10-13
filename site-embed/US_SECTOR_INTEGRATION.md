# US sector module: integration and deployment status

## Verified (2026-10-14)
- Live feed smoke run 38478005656 passed with 12/12 SPY + GICS ETF symbols observed on 2026-10-13.
- Validated history is committed to `main:data/us_sector_history.json`; do not rely on ephemeral Actions artifacts.
- A keyless snapshot publisher race removed the sector JSON; fixed by preserving only its own output in `.github/workflows/keyless.yml` (commit 26725756), then restored the validated sector JSON (commit 444a4bb3). Subsequent keyless update d6ddaf5c changed only `data/keyless_snapshot.json`.
- Sector tests on main passed: Actions run 38478972694.
- Existing API Worker regression passed: Actions run 38479232204.

## Backend contract
- Existing Worker source: `api-worker/index.mjs`.
- `GET /api/us-sector-report`: read-only public market context, powered by `site-embed/us-sector-loader.js` and the validated GitHub JSON.
- Returns `module: US_SECTOR_ROTATION_V1`, `status`, `classification`, `coverage`, `benchmark`, `observedAt`, `sectors`, `warnings`, `scoreContribution: 0`, `macroGateOverride: null`, `vetoOverride: null`.
- Missing or failed fetch => HTTP 200 with `status: UNKNOWN` and `errorCode: DATA_UNAVAILABLE`. Stale observations (>5 UTC calendar days) => `status: UNKNOWN`, `errorCode: STALE_DATA`. This is not a live trade signal.
- `GET /api/market-snapshot` retains private Bearer-token access and the original macro KV contract. Never put `SNAPSHOT_READ_TOKEN` in browser code.
- Sector output is separate, advisory context only; no duplicate scoring or VETO override.

## Remaining deployment tasks
1. Locate the existing Master Model production site's source or configured backend endpoint. This repository alone is not evidence that the original site has been updated.
2. Deploy the changed API Worker through its *existing* approved deployment process, after identifying the actual Worker project. The `wrangler.toml.example` is an example, not production credentials or a deployed route.
3. In the existing report pipeline, call `GET /api/us-sector-report` and attach the response as `usSectorContext` without changing existing UI, Macro Gate, 10D or VETO. On timeout or failure, attach UNKNOWN without blocking other sections.
4. Verify the production endpoint and original site output. No production deployment has been verified.

## Separate Pages issue
- The unrelated standalone quote-page workflow previously failed because GitHub Pages setup returned `Resource not accessible by integration`. Its automatic push trigger was removed (commit 86fee8fe); it remains manual-only, not an alternate replacement website.
