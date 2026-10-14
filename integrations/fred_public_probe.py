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
from decimal import Decimal, InvalidOperation
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
    if date_column is None or symbol not in columns or len(columns) != len(set(columns)):
        raise ValueError("official_csv_columns_invalid")
    points = {}
    rejected = 0
    for row in reader:
        try:
            observed = date.fromisoformat(row[date_column])
            if observed.isoformat() != row[date_column]:
                raise ValueError("noncanonical_date")
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
                   "unit": "percent", "frequency": "daily",
                   "definition_url": f"https://fred.stlouisfed.org/series/{symbol}",
                   "source_sha256": hashlib.sha256(raw).hexdigest(),
                   "retrieved_at": datetime.now(timezone.utc).isoformat()})
    return result


def cross_check_common_dates(results, *, tolerance_pp=0.02, today=None):
    """Same-provider definition consistency, not independent-source validation.

Compare only intersecting valid dates; never combine each series' latest row
or fill holidays. The 0.02 pp tolerance is an explicit diagnostic rounding
allowance, not a forecast, trading rule, score or OpenBB promotion gate.
    """
    today = today or datetime.now(timezone.utc).date()
    base = {"status": "unknown", "independent_source_verified": False,
            "equation": "DGS10 - DFII10 ~= T10YIE", "unit": "percentage_points",
            "definition_url": "https://fred.stlouisfed.org/series/T10YIE",
            "tolerance_pp": tolerance_pp, "score_contribution": 0}
    tolerance = Decimal(str(tolerance_pp))
    if not tolerance.is_finite() or tolerance < 0 or isinstance(tolerance_pp, bool):
        raise ValueError("invalid_rounding_tolerance")
    histories = {}
    for symbol in ALLOWED_SERIES:
        series = results.get(symbol)
        if not isinstance(series, dict) or series.get("status") != "ok":
            return {**base, "reason": f"{symbol}_unavailable_or_stale"}
        if series.get("unit") != "percent":
            return {**base, "reason": f"{symbol}_unit_not_verified"}
        points = series.get("history")
        if not isinstance(points, list) or not points:
            return {**base, "reason": f"{symbol}_history_missing"}
        history = {}
        for point in points:
            try:
                observed = date.fromisoformat(point["date"])
                value = Decimal(str(point["value"]))
                if observed.isoformat() != point["date"] or observed > today or not value.is_finite() or isinstance(point["value"], bool):
                    raise ValueError("invalid_observation")
                if observed in history and history[observed] != value:
                    raise ValueError("conflicting_duplicate_date")
                history[observed] = value
            except (TypeError, ValueError, KeyError, InvalidOperation):
                return {**base, "reason": f"{symbol}_invalid_history"}
        histories[symbol] = history
    common = sorted(set.intersection(*(set(h) for h in histories.values())))
    if not common:
        return {**base, "reason": "no_common_observation_dates"}
    if (today - common[-1]).days > 7:
        return {**base, "reason": "common_observation_date_stale", "as_of": common[-1].isoformat()}
    comparisons = []
    for observed in common:
        nominal, real, breakeven = (histories[s][observed] for s in ALLOWED_SERIES)
        implied = nominal - real
        residual = implied - breakeven
        comparisons.append({"date": observed.isoformat(), "DGS10": float(nominal),
                            "DFII10": float(real), "T10YIE": float(breakeven),
                            "implied_breakeven": float(implied), "residual_pp": float(residual),
                            "within_tolerance": abs(residual) <= tolerance})
    violations = [row for row in comparisons if not row["within_tolerance"]]
    latest = {s: max(histories[s]).isoformat() for s in ALLOWED_SERIES}
    return {**base, "status": "verified" if not violations else "watch",
            "reason": "same_date_values_consistent" if not violations else "same_date_definition_mismatch",
            "as_of": common[-1].isoformat(), "checked_dates": len(common),
            "latest_dates": latest, "latest_dates_aligned": len(set(latest.values())) == 1,
            "matched_dates": len(common) - len(violations), "mismatched_dates": len(violations),
            "comparisons": comparisons}


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
        except ValueError as error:
            results[symbol] = {"status": "missing", "error_type": "ValueError", "reason": str(error)[:120]}
        except Exception as error:
            results[symbol] = {"status": "missing", "error_type": type(error).__name__}
    valid = sum(row.get("status") == "ok" for row in results.values())
    return {"stage": "official_public_csv", "status": "verified" if valid == len(series) else "not_verified",
            "generated_at": datetime.now(timezone.utc).isoformat(), "series_count": len(series),
            "validated": valid, "results": results, "published": False,
            "common_date_check": cross_check_common_dates(results),
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
