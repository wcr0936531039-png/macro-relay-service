"""Read-only multi-series parity report. Never writes to the production snapshot.

Run in an isolated environment after installing OpenBB and setting FRED_API_KEY:
    python -m integrations.openbb_batch_parity DGS10 DFII10 T10YIE
"""
import json
import os
import sys
from integrations.openbb_parity import compare
from integrations.openbb_adapter import fetch_fred_series

DEFAULT_SERIES = ("DGS10", "DFII10", "T10YIE")


def check_batch(series_ids, official_fetch, candidate_fetch=fetch_fred_series):
    series_ids = list(series_ids)
    if not series_ids or len(set(series_ids)) != len(series_ids):
        return {"status": "not_verified", "reason": "empty_or_duplicate_series",
                "series_count": len(series_ids), "matched": 0, "results": {}, "published": False}
    results = {}
    for series_id in series_ids:
        try:
            results[series_id] = compare(series_id, official_fetch, candidate_fetch)
        except Exception as exc:
            results[series_id] = {"status": "unknown", "reason": "comparison_failed",
                                  "error_type": type(exc).__name__}
    statuses = [r["status"] for r in results.values()]
    return {"status": "match" if statuses and all(s == "match" for s in statuses) else "not_verified",
            "series_count": len(results),
            "matched": statuses.count("match"),
            "results": results,
            "published": False}


def main():
    from scripts.sync_macro import fred_observations
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise SystemExit("FRED_API_KEY missing")
    def official_fetch(symbol):
        rows = fred_observations(symbol, key, 12)
        if not rows:
            return {"status": "missing", "value": None, "date": None}
        return {"status": "ok", "value": rows[0]["value"],
                "date": rows[0]["date"], "source": "fred"}
    series = sys.argv[1:] or DEFAULT_SERIES
    report = check_batch(series, official_fetch)
    print(json.dumps(report, sort_keys=True))
    if report["status"] != "match":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
