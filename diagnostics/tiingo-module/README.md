# Tiingo private Site adapter — review copy, not a relay collector

Run from repository root:

```sh
node --test diagnostics/tiingo-module/tests/tiingo-market.test.mjs
```

11 mocked adapter/storage tests passed, including the late-bar bug, 22 tickers, SPY-required partial global breadth, aligned RSP/SPY dates, zero-fetch persistent cache, 429 cooldown, and real SQLite concurrent quota/lease guards. Python sqlite3 is required for the last test. All prices and credentials in tests are synthetic.

This directory is not wired into public workflows. No real Tiingo responses, prices or keys are included. Actual Site integration, fallback, UI and 38-test suite appear in the complete patch linked from diagnostics/latest.md. Apply only to original v229 baseline 543793fa6be1a9d4dfde79d0be4313eeb436f8e8. No deployment authorized or performed.

Complete patch: ../tiingo-integration/v229-local.patch
SHA256: 78cf08852783b9cf355568cdcb9d0ea417500fdb6383094808dc0a08b3b583d0
