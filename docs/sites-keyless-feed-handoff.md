# Sites data handoff: verified GitHub JSON feed

Published public feed (no API key required):
https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/data/stock_snapshots_v2.json

The JSON is schema_version=2 and has `stocks` keyed by ticker.
Each ticker contains `observations` with `metric`, `value`, `observed_at`, `source`, `source_url`, and `status`.
The four currently supported tickers are 8299, 5289, 2404, and 5009.
Metrics are daily close, volume_shares, and turnover_twd; do not infer EPS, ROIC, or valuation from these fields.

Integration recipe for the existing ChatGPT Site:
1. Fetch the URL from the Site's server-side data loader or backend, with a short timeout.
2. Validate schema_version=2, that `stocks[ticker]` exists, and that each observation's ticker matches the requested ticker.
3. For each metric, select the latest `status:ok` observation by observed_at. Never use the first element as latest.
4. Show observed_at separately from generated_at. If old, label stale and retain the last-known-good result.
5. On fetch failure, show data unavailable; do not invent values. Cache a previously validated snapshot where supported.
6. Merge the quote rows with separate official fundamentals only after those pipelines are implemented. Mark EPS, ROIC, financial statements, and valuations as missing in the meantime.
7. Keep the GitHub URL on the server side if possible. If used directly in browser code, test CORS and site platform outbound policy. No bearer token is needed for this public JSON.

The public Site address previously supplied:
https://taiwan-stock-master.fwf6fgj5p6.chatgpt.site

IMPORTANT: This repository change does not modify or deploy the Site. A Sites editor/Work session must attach the data loader and publish it. End-to-end verification requires inspecting the actual Site network response and rendered ticker cards.
