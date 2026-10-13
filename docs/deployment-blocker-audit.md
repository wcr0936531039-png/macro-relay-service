# Deployment blocker audit (2026-10-13)

## Verified repository state
- Default branch `main` contains `.github/workflows/keyless.yml` and `.github/workflows/sync_macro.yml`.
- Default branch does **not** contain `.github/workflows/deploy_staging_relay.yml`.
- The new staging deploy workflow exists only on `feature/master-model-v2-contract`.
- GitHub requires a `workflow_dispatch` workflow to exist on the default branch before manual dispatch can be used. A successful branch CI run is not a staging deployment.
- The existing `main` keyless publisher commits `data/keyless_snapshot.json` every six hours and is an independent data path. It does not automatically prove that the original ChatGPT Site consumes this file.
- The current stock V2 snapshots are not part of that keyless JSON contract and must not be represented as published.

## Safest next steps
1. Review PR #1 and merge only after validation and explicit approval, or introduce a minimal reviewed deployment workflow into the default branch.
2. Confirm four repository secrets are configured: `CF_ACCOUNT_ID`, `CF_API_TOKEN`, `CF_KV_NAMESPACE_ID`, and `SNAPSHOT_READ_TOKEN`. Never paste their values in chat or logs.
3. Trigger `Deploy staging relay (manual)` on the reviewed ref; capture the real deployment URL.
4. Probe `/api/stock-report?ticker=8299` without a bearer token (expect 401, not 404), then with the server-side token (expect 503 until KV is initialized, or a versioned JSON report).
5. Run the stock publisher with `DRY_RUN=false` only after confirming the KV namespace and credentials are for the intended environment. Verify readback.
6. Connect the original ChatGPT Site server-side proxy; do not expose `SNAPSHOT_READ_TOKEN` to client JavaScript.
7. Verify original Site shows the same snapshot timestamps and reports missing financials as missing.

Sources:
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow
- https://github.com/cloudflare/wrangler-action
