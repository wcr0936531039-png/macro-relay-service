"""Independent, read-only official FRED CSV diagnostics, never OpenBB parity.

The CLI saves only an isolated runner-temp artifact. It has no credentials,
snapshot publisher, fallback switch, or production integration.
"""
import csv
import hashlib
import io
import json
import math
import os
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ALLOWED_SERIES = ("DGS10", "DFII10", "T10YIE")


def parse_csv(text, symbol, *, today=None):
    if symbol not in ALLOWED_SERIES:
        raise ValueError("series_not_allowlisted")
    today = today or datetime.now(timezone.utc).date()
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    columns = reader.fieldnames or []
    date_column = next((c for c in columns if c.lower() in ("date", "observation_date")), None)
    if date_column is None or symbol not in columns:
        raise ValueError("official_csv_columns_invalid")
    points = {}
    rejected = 0
    for row in reader:
        try:
            observed = date.fromisoformat(row[date_column])
            value = float(row[symbol])
            if not math.isfinite(value) or observed > today:
                raise ValueError("invalid_observation")
        except (TypeError, ValueError, KeyError, OverflowError):
            rejected += 1
            continue
        if observed in points and points[observed] != value:
            raise ValueError("conflicting_duplicate_date")
        points[observed] = value
    if not points:
        raise ValueError("no_valid_observations")
    history = [{"date": d.isoformat(), "value": points[d]} for d in sorted(points)]
    latest = history[-1]
    age = (today - date.fromisoformat(latest["date"])).days
    return {"status": "ok" if age <= 7 else "stale", "latest": latest,
            "observations": len(history), "rejected_rows": rejected,
            "age_calendar_days": age, "history": history}


def fetch_public_series(symbol):
    if symbol not in ALLOWED_SERIES:
        raise ValueError("series_not_allowlisted")
    since = (datetime.now(timezone.utc).date() - timedelta(days=90)).isoformat()
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?" + urlencode({"id": symbol, "cosd": since})
    request = Request(url, headers={"User-Agent": "MacroRelay-IsolatedFredProbe/1.0",
                                    "Accept": "text/csv"})
    with urlopen(request, timeout=25) as response:
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("response_too_large")
        final_url = response.geturl()
        if not final_url.startswith("https://fred.stlouisfed.org/graph/fredgraph.csv?"):
            raise ValueError("unexpected_source_redirect")
        http_status = response.status
    result = parse_csv(raw.decode("utf-8-sig"), symbol)
    result.update({"symbol": symbol, "source": url, "http_status": http_status,
                   "source_sha256": hashlib.sha256(raw).hexdigest(),
                   "retrieved_at": datetime.now(timezone.utc).isoformat()})
    return result


def probe_batch(series, fetch=fetch_public_series):
    series = list(series)
    if not series or len(series) != len(set(series)) or any(s not in ALLOWED_SERIES for s in series):
        raise ValueError("invalid_series_selection")
    results = {}
    for symbol in series:
        try:
            results[symbol] = fetch(symbol)
        except HTTPError as error:
            results[symbol] = {"status": "missing", "error_type": "HTTPError", "http_status": error.code}
        except URLError:
            results[symbol] = {"status": "missing", "error_type": "URLError"}
        except Exception as error:
            results[symbol] = {"status": "missing", "error_type": type(error).__name__}
    valid = sum(row.get("status") == "ok" for row in results.values())
    return {"stage": "official_public_csv", "status": "verified" if valid == len(series) else "not_verified",
            "generated_at": datetime.now(timezone.utc).isoformat(), "series_count": len(series),
            "validated": valid, "results": results, "published": False,
            "openbb_live_parity_verified": False, "fallback_enabled": False}


def main():
    report = probe_batch(sys.argv[1:] or ALLOWED_SERIES)
    audit_root = Path(os.environ.get("RUNNER_TEMP") or tempfile.gettempdir()) / "openbb-isolated"
    audit_root.mkdir(parents=True, exist_ok=True)
    (audit_root / "official-public-fred.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    if report["status"] != "verified":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
