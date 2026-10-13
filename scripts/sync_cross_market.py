"""Independent, no-key history feed for the existing Taiwan Master Model.

No estimates are invented here. EPS revisions are evaluated per company by the
Site against its verified consensus archive. Failed providers remain missing.
"""
import csv
import io
import json
import math
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data/cross_market_snapshot.json"
UA = "Mozilla/5.0 (compatible; TaiwanStockMaster/1.0; public EOD research)"
UTC = timezone.utc
NOW = datetime.now(UTC)


def number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        n = float(str(value).replace(",", "").replace("$", "").replace("%", "").replace("−", "-").strip())
        return n if math.isfinite(n) else None
    except (TypeError, ValueError):
        return None


def iso_date(value):
    text = str(value or "").strip()
    match = re.fullmatch(r"(\d{3,4})[/-]?(\d{2})[/-]?(\d{2})", text)
    if not match:
        return None
    y, m, d = map(int, match.groups())
    if y < 1911:
        y += 1911
    try:
        return date(y, m, d).isoformat()
    except ValueError:
        return None


def available_at(day, market):
    hour, minute, zone = (13, 30, "Asia/Taipei") if market == "TW" else (16, 15, "America/New_York")
    return datetime.fromisoformat(day).replace(hour=hour, minute=minute, tzinfo=ZoneInfo(zone)).astimezone(UTC).isoformat()


def fetch_text(url):
    last = None
    for attempt in range(2):
        try:
            req = Request(url, headers={"User-Agent": UA, "Accept": "application/json,text/csv,*/*", "Referer": "https://www.twse.com.tw/" if "twse.com" in url else "https://www.nasdaq.com/"})
            with urlopen(req, timeout=18) as response:
                body = response.read(5_000_001)
            if len(body) > 5_000_000:
                raise ValueError("response exceeds 5 MB")
            return body.decode("utf-8-sig")
        except Exception as error:
            last = error
            if attempt == 0:
                time.sleep(.3)
    raise ValueError(str(last))


def fetch_json(url):
    return json.loads(fetch_text(url))


def unique_points(points):
    by_day = {}
    for point in points:
        if iso_date(point.get("date")) and number(point.get("value")) is not None and point["value"] > 0 and datetime.fromisoformat(point["available_at"]) <= NOW:
            if point["date"] in by_day and by_day[point["date"]]["value"] != point["value"]:
                raise ValueError("conflicting duplicate closing price")
            by_day[point["date"]] = point
    return sorted(by_day.values(), key=lambda p: p["date"])[-100:]


def fred_history(sid):
    start = (NOW.date() - timedelta(days=190)).isoformat()
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={start}"
    rows = csv.DictReader(io.StringIO(fetch_text(url)))
    points = []
    for row in rows:
        day = iso_date(row.get("observation_date") or row.get("DATE"))
        value = number(row.get(sid))
        if day and value is not None and value > 0:
            points.append({"date": day, "value": value, "available_at": available_at(day, "US")})
    return {"history": unique_points(points), "source": url, "provider": f"FRED official published price-index history | {sid}", "market": "US", "unit": "index_points"}


def twse_month(payload, source):
    if payload.get("stat") != "OK":
        raise ValueError("TWSE FMTQIK status is not OK")
    fields = payload.get("fields", [])
    indices = [next((i for i, f in enumerate(fields) if token in str(f)), None) for token in ("日期", "發行量加權股價指數", "成交金額")]
    if any(i is None for i in indices):
        raise ValueError("TWSE FMTQIK expected date/index/turnover fields")
    points = []
    for row in payload.get("data", []):
        if len(row) <= max(indices):
            continue
        day, close, turnover = iso_date(row[indices[0]]), number(row[indices[1]]), number(row[indices[2]])
        if day and close is not None and close > 0 and turnover is not None and turnover >= 0:
            points.append({"date": day, "value": close, "totalValueTwd": turnover, "available_at": available_at(day, "TW"), "source": source})
    return points


def taiwan_history():
    points, warnings, sources = [], [], []
    for offset in range(3):
        month = NOW.year * 12 + NOW.month - 1 - offset
        y, m = divmod(month, 12)
        compact = f"{y}{m + 1:02d}01"
        url = f"https://www.twse.com.tw/exchangeReport/FMTQIK?date={compact}&response=json"
        try:
            points.extend(twse_month(fetch_json(url), url))
            sources.append(url)
        except Exception as error:
            warnings.append(f"{compact}: {error}")
    return {"history": unique_points(points), "source": sources[0] if sources else "https://www.twse.com.tw/", "sources": sources, "provider": "TWSE official FMTQIK | TAIEX price index", "market": "TW", "unit": "index_points", "warnings": warnings}


def parse_sox_nasdaq(body, source):
    data = body.get("data") or {}
    if str(data.get("symbol", "")).upper() != "SOX":
        raise ValueError("Nasdaq SOX symbol mismatch")
    points = []
    for row in (data.get("tradesTable") or {}).get("rows", []):
        try:
            day = datetime.strptime(row["date"], "%m/%d/%Y").date().isoformat()
        except (KeyError, ValueError, TypeError):
            continue
        value = number(row.get("close") or row.get("value"))
        if value is not None and value > 0:
            points.append({"date": day, "value": value, "available_at": available_at(day, "US")})
    return {"history": unique_points(points), "source": source, "provider": "Nasdaq official SOX historical prices", "market": "US", "unit": "index_points"}


def parse_sox_yahoo(body, source):
    result = (body.get("chart", {}).get("result") or [None])[0]
    if not isinstance(result, dict) or result.get("meta", {}).get("symbol") != "^SOX" or result.get("meta", {}).get("exchangeTimezoneName") != "America/New_York":
        raise ValueError("Yahoo SOX symbol/timezone mismatch")
    closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
    points = []
    for i, stamp in enumerate(result.get("timestamp", [])):
        value = number(closes[i]) if i < len(closes) else None
        if value is None or value <= 0:
            continue
        day = datetime.fromtimestamp(stamp, ZoneInfo("America/New_York")).date().isoformat()
        points.append({"date": day, "value": value, "available_at": available_at(day, "US")})
    return {"history": unique_points(points), "source": source, "provider": "Yahoo Finance | delayed SOX price-index history (third party)", "market": "US", "unit": "index_points"}


def sox_history():
    official = "https://api.nasdaq.com/api/quote/SOX/historical?assetclass=index&limit=120"
    alternative = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote('^SOX', safe='')}?range=6mo&interval=1d"
    errors = []
    for parser, url in ((parse_sox_nasdaq, official), (parse_sox_yahoo, alternative)):
        try:
            result = parser(fetch_json(url), url)
            if len(result["history"]) < 21:
                raise ValueError("SOX has fewer than 21 completed closes")
            result["warnings"] = errors
            return result
        except Exception as error:
            errors.append(f"{url}: {error}")
    raise ValueError("; ".join(errors))


def assert_twse_date(payload, day):
    if payload.get("stat") != "OK" or iso_date(payload.get("date")) != day:
        raise ValueError("TWSE response date/status mismatch")


def institution_flows(payload, day):
    assert_twse_date(payload, day)
    fields = payload.get("fields", [])
    col = next((i for i, f in enumerate(fields) if "買賣差額" in str(f)), None)
    if col is None:
        raise ValueError("BFI82U net TWD column absent")
    result = {}
    for row in payload.get("data", []):
        if len(row) <= col:
            continue
        label = str(row[0]).replace("（", "(").replace("）", ")").replace(" ", "")
        if label.startswith("外資及陸資") and "不含外資自營商" in label:
            result["foreignNetTwd"] = number(row[col])
        elif label == "投信":
            result["investmentTrustNetTwd"] = number(row[col])
    if any(result.get(k) is None for k in ("foreignNetTwd", "investmentTrustNetTwd")):
        raise ValueError("BFI82U foreign/trust observations absent")
    return result


def daytrade_value(payload, day):
    assert_twse_date(payload, day)
    tables = payload.get("tables") or [{"fields": payload.get("fields", []), "data": payload.get("data", [])}]
    for table in tables:
        fields = table.get("fields", [])
        buy = next((i for i, f in enumerate(fields) if "買進" in str(f) and "金額" in str(f)), None)
        sell = next((i for i, f in enumerate(fields) if "賣出" in str(f) and "金額" in str(f)), None)
        if buy is None or sell is None:
            continue
        data = table.get("data") or []
        if not data:
            continue
        # Use the market summary table, or sum security rows without counting a
        # total row twice. Volume percentages never proxy for value percentages.
        summary = not any("證券代號" in str(f) for f in fields)
        records = data[:1] if summary else [row for row in data if "合計" not in str(row[0])]
        buys, sells = [], []
        for row in records:
            b, s = number(row[buy]), number(row[sell])
            if b is None or s is None or b < 0 or s < 0:
                raise ValueError("day-trade amounts incomplete")
            buys.append(b); sells.append(s)
        if buys:
            return {"dayTradeBuyTwd": sum(buys), "dayTradeSellTwd": sum(sells), "dayTradeValueTwd": (sum(buys) + sum(sells)) / 2}
    raise ValueError("TWTB4U matched buy/sell amount columns absent")


def flows(tw, previous):
    saved = {p["date"]: p for p in previous.get("flows", {}).get("history", []) if p.get("status") == "ok"}
    rows = []
    for point in tw.get("history", [])[-10:]:
        day = point["date"]
        if day in saved and saved[day].get("totalValueTwd") == point["totalValueTwd"]:
            rows.append(saved[day]); continue
        compact = day.replace("-", "")
        inst_url = f"https://www.twse.com.tw/exchangeReport/BFI82U?dayDate={compact}&type=day&response=json"
        day_url = f"https://www.twse.com.tw/exchangeReport/TWTB4U?date={compact}&selectType=All&response=json"
        row = {"date": day, "fetched_at": NOW.isoformat(), "totalValueTwd": point["totalValueTwd"], "status": "ok", "sources": [point["source"], inst_url, day_url], "scope": "TWSE_all_listed_securities"}
        for fn, url in ((institution_flows, inst_url), (daytrade_value, day_url)):
            try:
                row.update(fn(fetch_json(url), day))
            except Exception as error:
                row["status"] = "partial"; row.setdefault("errors", []).append(str(error))
        if number(row.get("dayTradeValueTwd")) is not None:
            non = row["totalValueTwd"] - row["dayTradeValueTwd"]
            row["nonDayTradeValueTwd"] = non if non >= 0 else None
            if non < 0:
                row["status"] = "partial"; row.setdefault("errors", []).append("day-trade value exceeds total value")
        rows.append(row)
    return {"history": rows, "scope": "TWSE_all_listed_securities", "method": "nonDayTradeValueTwd = FMTQIK total value minus (TWTB4U day-trade buy value + sell value)/2; institutions are BFI82U net TWD"}


def build(previous=None):
    previous = previous or {}
    snapshot = {"schema_version": 1, "generated_at": NOW.isoformat(), "basis": "local_currency_price_index", "markets": {}, "errors": []}
    for sid, fn in (("TWSE_TAIEX", taiwan_history), ("SP500", lambda: fred_history("SP500")), ("NASDAQCOM", lambda: fred_history("NASDAQCOM")), ("SOX", sox_history)):
        try:
            entry = fn()
            if len(entry["history"]) < 21:
                raise ValueError(f"only {len(entry['history'])}/21 completed closes")
            entry.update(status="ok", fetched_at=NOW.isoformat())
        except Exception as error:
            entry = {**previous.get("markets", {}).get(sid, {}), "status": "stale" if previous.get("markets", {}).get(sid) else "missing", "error": str(error)}
            snapshot["errors"].append({"id": sid, "error": str(error)})
        snapshot["markets"][sid] = entry
    try:
        snapshot["flows"] = flows(snapshot["markets"]["TWSE_TAIEX"], previous)
    except Exception as error:
        snapshot["flows"] = {"history": [], "error": str(error)}
    snapshot["status"] = "ok" if not snapshot["errors"] and len(snapshot["flows"]["history"]) == 10 and all(x["status"] == "ok" for x in snapshot["flows"]["history"]) else "partial"
    return snapshot


def main():
    previous = json.loads(DEST.read_text()) if DEST.exists() else {}
    payload = build(previous)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": payload["status"], "histories": {k: len(v.get("history", [])) for k, v in payload["markets"].items()}, "flows": len(payload["flows"]["history"]), "errors": payload["errors"], "flow_gaps": [{"date": r["date"], "errors": r.get("errors", [])} for r in payload["flows"]["history"] if r["status"] != "ok"]}, ensure_ascii=False))
    return 0  # Provider gaps are data states, not a failure of independent jobs.


if __name__ == "__main__":
    sys.exit(main())
