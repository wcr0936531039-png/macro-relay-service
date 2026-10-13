# US sector module: integration contract

## Verified on 2026-10-14
- GitHub Actions live smoke run 38478005656 passed: SPY plus 11 sector ETFs, observed_at 2026-10-13, 12/12 coverage, no issues.
- Validated JSON uploaded as run artifact 11856650418.
- Unit test run 38478005591 passed.
- The smoke artifact is NOT a production endpoint.

## Production path (after PR merge)
1. Workflow `.github/workflows/us-sector-history.yml` runs on default branch (scheduled workflows do not run from feature branches).
2. It fetches 12 symbols and runs `scripts/check_us_sector_snapshot.py`; on failure, do not commit the JSON.
3. On success, commits `data/us_sector_history.json` to the default branch.
4. Existing site's backend can call `loadUSSectorReport()` from `site-embed/us-sector-loader.js`, which reads the raw GitHub JSON. Note GitHub raw CDN caching: consumers should handle freshness and preserve last known good status without treating stale data as live.
5. Attach the report as `usSectorContext` to existing report output; do not alter original UI, Macro Gate, 10D, VETO, or other scoring. If unavailable, display UNKNOWN.

## Remaining integration
- The existing production website code is not in this PR; no site deployment has occurred.
- Production data publishing requires merging this PR into main and a successful scheduled or manual workflow run.
- Validate public raw JSON accessibility and final site report in production before calling the deployment complete.
