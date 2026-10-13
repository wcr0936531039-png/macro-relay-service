# ChatGPT Sites integration handoff

This repository is a data relay, not the editable ChatGPT Sites project. No site deployment is implied.

## Required environment
- Deploy `api-worker/index.mjs` with a `MACRO_KV` binding and `SNAPSHOT_READ_TOKEN` secret.
- GitHub Actions publishing requires Cloudflare account ID, KV namespace ID, and a scoped API token.
- Never put the read token in browser JavaScript or in a public site setting.

## Server-side Sites proxy
The Sites application needs a server-side route, e.g. `/api/site-stock-report?ticker=8299`, which:
1. Validates a four-to-six-digit ticker.
2. Fetches the deployed private Worker `/api/stock-report?ticker=...` with a server-side bearer token.
3. Forwards JSON and HTTP status without converting missing or stale data into a success.
4. Returns a controlled 503 error if the Worker is unavailable.

If the Sites environment cannot hold secrets or implement server routes, a browser must not call the private Worker with the bearer token. Instead create a public, read-only gateway that exposes only sanitized, non-sensitive stock snapshots with strict origin and rate controls.

## Report rendering
- `report.observations`: prices, volume and turnover, with source and observation date.
- `report.coverage.metrics`: show unavailable financial metrics explicitly.
- `report.final_rating`: must remain null until independent modules pass.
- `status=stale`: show last-known-good data and a visible freshness warning.

## Acceptance checks
1. Official TWSE/TPEx read-only probe passes for all four tracked tickers.
2. Manually publish a non-production KV namespace, then GET the same key to confirm byte-level persistence.
3. Deploy Worker with that namespace and verify 401 without token and 200 with valid token.
4. Verify each stock report and unchanged macro route from the server.
5. Connect the Sites server proxy; verify network tab shows a 200/503 as appropriate.
6. Confirm no bearer token appears in public browser responses or bundles.
7. Only then enable automatic production publishing.

Current state: GitHub branch and PR contain integration code. No confirmed Cloudflare write, Worker deployment or Sites editing access.
