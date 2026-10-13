"""Read-only live parity check; never publishes or modifies snapshots.

Usage (isolated runner with OpenBB installed and FRED_API_KEY configured):
    python -m integrations.openbb_parity DGS10
"""
import json
import os
import sys

from integrations.openbb_adapter import fetch_fred_series
from integrations.openbb_arbitration import choose_observation


def compare(series_id, official_fetch, candidate_fetch=fetch_fred_series):
    """Check date/value parity with the authoritative FRED observation."""
    try:
        official = official_fetch(series_id)
    except Exception as exc:
        return {"status": "unknown", "reason": "official_fetch_failed", "error_type": type(exc).__name__}
    candidate = candidate_fetch(series_id)
    chosen, reason = choose_observation(official, candidate)
    if chosen is None:
        return {"status": "unknown", "reason": reason,
                "official_status": official.get("status") if isinstance(official, dict) else None,
                "candidate_status": candidate.get("status") if isinstance(candidate, dict) else None}
    if candidate.get("status") != "ok":
        return {"status": "unknown", "reason": "candidate_unavailable",
                "official_date": chosen["date"], "candidate_error": candidate.get("error")}
    if chosen["date"] != candidate.get("date"):
        return {"status": "mismatch", "reason": "observation_date_differs",
                "official_date": chosen["date"], "candidate_date": candidate.get("date")}
    if abs(float(chosen["value"]) - float(candidate["value"])) > 1e-8:
        return {"status": "mismatch", "reason": "observation_value_differs",
                "official_date": chosen["date"], "official_value": chosen["value"],
                "candidate_value": candidate["value"]}
    return {"status": "match", "reason": "same_date_and_value", "date": chosen["date"],
            "value": chosen["value"]}


def main():
    from scripts.sync_macro import fred_observations
    series_id = sys.argv[1] if len(sys.argv) > 1 else "DGS10"
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise SystemExit("FRED_API_KEY missing")
    def official_fetch(symbol):
        rows = fred_observations(symbol, key, 12)
        if not rows:
            return {"status": "missing", "value": None, "date": None}
        return {"status": "ok", "value": rows[0]["value"], "date": rows[0]["date"], "source": "fred"}
    result = compare(series_id, official_fetch)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result["status"] != "match":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
