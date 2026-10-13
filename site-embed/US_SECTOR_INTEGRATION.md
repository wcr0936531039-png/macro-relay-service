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

## Non-mutating report integration adapter
- Import `attachUSSectorContext` from `site-embed/us-sector-context.js` in the existing report backend.
- Usage: `const enrichedReport = await attachUSSectorContext(existingReport, fetch, new Date());`
- The adapter returns a new report object with `usSectorContext`; it does not mutate the original report, score, Macro Gate, 10D or VETO.
- If the source is unavailable, the context has `status: UNKNOWN` and `errorCode: DATA_UNAVAILABLE`; scoring stays unchanged.
- Unit test: `node --test site-embed/us-sector-context.test.mjs`.
- This is integration-ready source code, **not proof that the separate original production site has been modified**.

## Preferred direct integration for the existing managed Site (no Cloudflare Worker required)

The validated GitHub JSON is public; **US sector context does not depend on deploying `api-worker/index.mjs` or Cloudflare KV**. If the original Site's server-side report code can import this module, integrate it at the report assembly boundary without changing routes, UI components, Macro Gate, 10D, VETO or scores:

```js
import {attachUSSectorContext} from './us-sector-context.js';

// existingReport must already have been calculated by the Site's own model.
const enrichedReport = await attachUSSectorContext(existingReport, fetch, new Date());
// Return enrichedReport from the existing report route; DO NOT create a new page.
```

The adapter reads `https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/data/us_sector_history.json` with an 8-second abort signal, returns `UNKNOWN` if unavailable or stale, and never overrides existing decisions. This is a **server integration recipe**, not an assertion that the inaccessible managed Site has been edited. Confirm its backend can perform outbound `fetch` and supports ECMAScript module imports before use; if the platform cannot import files, adapt the same logic in its existing report handler rather than redirecting to a new website.

**Evidence required for production sign-off:** identify the actual Site editor/source and publishing target, verify the original report request returns `usSectorContext` while original fields and UI remain intact, verify failure behavior, and record the deployed revision and a production response. Until then mark `SITE_NOT_CONNECTED` and `DEPLOYMENT_UNVERIFIED`, regardless of GitHub CI status.

The separate Worker endpoint is optional for US sector context. `/api/market-snapshot` remains private and has distinct token/KV requirements; do not weaken those requirements or expose its bearer token.
