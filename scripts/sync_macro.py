#!/usr/bin/env python3
"""Fetch official macro observations and publish one validated snapshot to Cloudflare KV.

Required environment: FRED_API_KEY, CF_ACCOUNT_ID, CF_KV_NAMESPACE_ID, CF_API_TOKEN.
Use --dry-run to validate/fetch without Cloudflare access; --previous accepts a local snapshot.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

SCHEMA_VERSION = 1
SNAPSHOT_KEY = "market_snapshot"
USER_AGENT = "TaiwanStockMaster-MacroRelay/1.0 (scheduled official-data snapshot)"
FRED_API = "https://api.stlouisfed.org/fred/series/observations"
MOEA_URL = "https://service.moea.gov.tw/EE521/common/Common.aspx?code=B&no=1"
NDC_NEWS_URL = "https://www.ndc.gov.tw/News9_1.aspx?n=257D28E6C2DCC0F8&sms=EC9205F763E2A607"
NDC_URL = "https://index.ndc.gov.tw/n/json/lightscore"
TPEX_URL = "https://www.tpex.org.tw/openapi/v1/tpex_mainborad_highlight"


def valid_number(value: Any) -> bool:
    """Accept 0 and numeric strings; reject empty, dot, booleans, NaN and infinity."""
    if value is None or isinstance(value, bool) or value == "" or value == ".":
        return False
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return number == number and abs(number) != float("inf")


def http_json(url: str, *, method: str = "GET", data: bytes | None = None,
              headers: dict[str, str] | None = None, timeout: int = 25) -> Any:
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json, text/html;q=0.9, */*;q=0.8"}
    if headers:
        request_headers.update(headers)
    request = Request(url, data=data, headers=request_headers, method=method)
    with urlopen(request, timeout=timeout) as response:
        body = response.read(8_000_001)
        if len(body) > 8_000_000:
            raise ValueError("上游回應超過 8 MB")
        content_type = response.headers.get("Content-Type", "")
    if "json" not in content_type.lower() and not body.lstrip().startswith((b"{", b"[")):
        raise ValueError(f"上游未回傳 JSON（Content-Type: {content_type or 'unknown'}）")
    return json.loads(body)


def http_text(url: str, *, headers: dict[str, str] | None = None, timeout: int = 25) -> str:
    request_headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"}
    if headers:
        request_headers.update(headers)
    with urlopen(Request(url, headers=request_headers), timeout=timeout) as response:
        body = response.read(5_000_001)
        if len(body) > 5_000_000:
            raise ValueError("官方頁面超過 5 MB")
        content_type = response.headers.get("Content-Type", "")
    if "html" not in content_type.lower() and not re.search(rb"<html|<table|<tr", body, re.I):
        raise ValueError(f"上游未回傳可解析 HTML（Content-Type: {content_type or 'unknown'}）")
    return body.decode("utf-8", errors="replace")


def fred_observations(series_id: str, api_key: str, limit: int = 8) -> list[dict[str, Any]]:
    query = urlencode({"series_id": series_id, "api_key": api_key, "file_type": "json",
                       "sort_order": "desc", "limit": str(limit)})
    payload = http_json(f"{FRED_API}?{query}")
    if payload.get("error_code"):
        raise ValueError(f"FRED {payload.get('error_code')}: {payload.get('error_message', 'request failed')}")
    observations = payload.get("observations")
    if not isinstance(observations, list):
        raise ValueError("FRED observations 欄位格式不符")
    rows = [{"date": str(item.get("date", "")), "value": float(item["value"])}
            for item in observations
            if isinstance(item, dict) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(item.get("date", "")))
            and valid_number(item.get("value"))]
    return sorted(rows, key=lambda x: x["date"], reverse=True)


def month_number(date: str) -> int:
    match = re.fullmatch(r"(\d{4})-(\d{2})-\d{2}", date)
    if not match:
        raise ValueError(f"無效的月資料日期：{date}")
    year, month = map(int, match.groups())
    return year * 12 + month


def metric(value: float | None, date: str | None, *, unit: str, provider: str,
           source: str, method: str, status: str = "ok", **extra: Any) -> dict[str, Any]:
    return {"value": value, "date": date, "unit": unit, "status": status,
            "provider": provider, "source": source, "method": method, **extra}


def fred_metric(series_id: str, api_key: str, *, unit: str, name: str | None = None,
                limit: int = 8) -> dict[str, Any]:
    obs = fred_observations(series_id, api_key, limit)
    if not obs:
        raise ValueError(f"{series_id} 沒有有效觀測值")
    latest = obs[0]
    return metric(latest["value"], latest["date"], unit=unit,
                  provider=f"FRED 官方 API｜{series_id}",
                  source=f"https://fred.stlouisfed.org/series/{series_id}",
                  method=name or f"採用 {series_id} 最新有效觀測；「.」不視為數值")


def nfp_metric(api_key: str) -> dict[str, Any]:
    obs = fred_observations("PAYEMS", api_key, 8)
    if len(obs) < 2 or month_number(obs[0]["date"]) - month_number(obs[1]["date"]) != 1:
        raise ValueError("PAYEMS 最近兩筆不是相鄰月份，拒絕計算非農月增")
    value = obs[0]["value"] - obs[1]["value"]
    return metric(value, obs[0]["date"], unit="千人", provider="FRED 官方 API｜PAYEMS",
                  source="https://fred.stlouisfed.org/series/PAYEMS",
                  method="總非農就業人數本月減前月；PAYEMS 單位為千人",
                  prior_date=obs[1]["date"], prior_value=obs[1]["value"])


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.rows: list[list[str]] = []; self.row: list[str] = []
        self.cell: list[str] | None = None
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "tr": self.row = []
        elif tag.lower() in ("td", "th"): self.cell = []
    def handle_data(self, data: str) -> None:
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split())); self.cell = None
        elif tag.lower() == "tr" and self.row:
            self.rows.append(self.row)


def taiwan_export_metric(html: str) -> dict[str, Any]:
    parser = TableParser(); parser.feed(html)
    year: int | None = None; candidates: list[tuple[str, float]] = []
    for cells in parser.rows:
        joined = " ".join(cells)
        ym = re.search(r"(?:民國\s*)?(\d{2,3})\s*年", joined)
        if ym: year = int(ym.group(1)) + 1911
        mm = re.search(r"(?:^|\s)(\d{1,2})\s*月(?:\s|$)", joined)
        if not mm or not year or re.search(r"1\s*-\s*\d{1,2}\s*月", joined): continue
        month = int(mm.group(1))
        if month not in range(1, 13): continue
        # Table order is month, USD amount, USD YoY, TWD amount, TWD YoY.
        # Select the first YoY column (USD), matching the dashboard definition.
        month_index = next((i for i, cell in enumerate(cells) if re.search(r"\d{1,2}\s*月", cell)), None)
        if month_index is None: continue
        numbers: list[float] = []
        for cell in cells[month_index + 1:]:
            raw = cell.strip().replace(",", "")
            if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", raw):
                numbers.append(float(raw))
            elif re.fullmatch(r"[-+]?\d{1,3}(?:\s+\d{3})+(?:\.\d+)?", raw):
                numbers.append(float(re.sub(r"\s+", "", raw)))
        if len(numbers) >= 2 and numbers[1] >= -100:
            candidates.append((f"{year}-{month:02d}-01", numbers[1]))
    if not candidates: raise ValueError("經濟部官方表格找不到有效單月外銷訂單年增率")
    date, value = max(candidates)
    return metric(value, date, unit="%", provider="經濟部統計處｜外銷訂單統計",
                  source=MOEA_URL, method="官方月表單月外銷訂單年增率；排除累計列")


def ndc_metric(payload: dict[str, Any]) -> dict[str, Any]:
    points = payload.get("line")
    points = [p for p in points if isinstance(p, dict) and re.fullmatch(r"\d{6}", str(p.get("x", "")))
              and valid_number(p.get("y"))] if isinstance(points, list) else []
    if not points: raise ValueError("國發會 JSON 缺少有效月度分數")
    point = max(points, key=lambda p: p["x"]); period = str(point["x"])
    score = float(point["y"]); month = int(period[4:]); year = int(period[:4])
    if month not in range(1, 13) or not 9 <= score <= 45: raise ValueError("國發會月份或燈號分數超出官方範圍")
    light = "紅燈" if score >= 38 else "黃紅燈" if score >= 32 else "綠燈" if score >= 23 else "黃藍燈" if score >= 17 else "藍燈"
    return metric(score, f"{year}-{month:02d}-01", unit="分", provider="國家發展委員會｜景氣指標查詢系統",
                  source=NDC_URL, method="官方綜合判斷分數及對應燈號", light=light)


class NdcNewsParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.href = None; self.label = []; self.text = []
    def handle_starttag(self, tag, attrs):
        if tag == "a": self.href = dict(attrs).get("href"); self.label = []
    def handle_data(self, data):
        self.text.append(data)
        if self.href: self.label.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.href:
            self.links.append((self.href, "".join(self.label)))
            self.href = None


def ndc_news_metric(html, source):
    parser = NdcNewsParser(); parser.feed(html)
    text = re.sub(r"\s+", "", "".join(parser.text))
    pattern = r"(\d{3})年(\d{1,2})月(?:份)?景氣對策信號綜合判斷分數為(\d{1,2})分"
    candidates = []
    for year, month, score in re.findall(pattern, text):
        if 1 <= int(month) <= 12 and 9 <= int(score) <= 45:
            candidates.append((f"{int(year)+1911}{int(month):02d}", int(score)))
    if not candidates: raise ValueError("官方新聞稿沒有可確認的觀測月份及綜合分數")
    period, score = max(candidates)
    row = ndc_metric({"line": [{"x": period, "y": score}]})
    row.update(provider="國家發展委員會｜官方景氣概況新聞稿", source=source,
               method="從官方新聞稿正文擷取觀測月份及綜合判斷分數；非發布月份")
    return row


def fetch_ndc():
    try:
        payload = http_json(NDC_URL, method="POST", data=b"", headers={"Origin": "https://index.ndc.gov.tw", "Referer": "https://index.ndc.gov.tw/n/zh_tw", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"})
        return ndc_metric(payload)
    except Exception as primary:
        primary_error = str(primary)
    try:
        html = http_text(NDC_NEWS_URL)
        parser = NdcNewsParser(); parser.feed(html)
        links = []
        for href, label in parser.links:
            match = re.search(r"(\d{3})年(\d{1,2})月份景氣概況新聞稿", label)
            url = urljoin(NDC_NEWS_URL, href)
            if match and urlparse(url).hostname == "www.ndc.gov.tw" and urlparse(url).scheme == "https":
                links.append((int(match[1])*12+int(match[2]), url))
        if not links: raise ValueError("國發會列表沒有可確認的月度新聞稿連結")
        _, url = max(links)
        row = ndc_news_metric(http_text(url), url)
        row["upstream_warning"] = "主要 JSON 來源失敗：" + primary_error
        return row
    except Exception as secondary:
        raise ValueError(f"NDC JSON: {primary_error}; 官方新聞稿備援: {secondary}") from secondary


def parse_roc_date(raw: Any) -> str | None:
    text = str(raw or "").strip()
    m = re.fullmatch(r"(\d{3})(\d{2})(\d{2})", text)
    if m: return f"{int(m[1])+1911}-{m[2]}-{m[3]}"
    m = re.fullmatch(r"(\d{3,4})[/\-]?(\d{1,2})[/\-]?(\d{1,2})", text)
    if not m: return None
    year = int(m[1]); year = year + 1911 if year < 1911 else year
    try: return f"{year:04d}-{int(m[2]):02d}-{int(m[3]):02d}"
    except ValueError: return None


def tpex_metric(rows: Any) -> dict[str, Any]:
    if not isinstance(rows, list): raise ValueError("TPEx OpenAPI 回傳格式非陣列")
    parsed = []
    for row in rows:
        if not isinstance(row, dict): continue
        date = parse_roc_date(row.get("Date", row.get("date", row.get("日期"))))
        def field(names: tuple[str, ...], pattern: str) -> Any:
            for key, value in row.items():
                if key in names or re.search(pattern, key, re.I): return value
            return None
        up = field(("PriceRiseCompanyNumbers", "Advance", "上漲家數"), r"advance|rise.*company|上漲")
        down = field(("PriceDeclineCompanyNumbers", "Decline", "下跌家數"), r"declin|down.*company|下跌")
        if date and valid_number(up) and valid_number(down) and float(up)+float(down)>0:
            parsed.append((date, float(up), float(down)))
    if not parsed: raise ValueError("TPEx 回應沒有可核對的日期及漲跌家數")
    date, up, down = max(parsed)
    return metric(up/(up+down)*100, date, unit="%", provider="櫃買中心 TPEx OpenAPI",
                  source=TPEX_URL, method="上漲家數 ÷（上漲＋下跌）× 100；只計上櫃股票",
                  advancers=int(up), decliners=int(down))


def current_metric_set(api_key: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    fred_specs = {
        "SOFR": ("SOFR", "%"), "ON_RRP": ("RRPONTSYD", "十億美元"),
        "REPO_TEMPORARY_OPERATIONS": ("RPONTSYD", "十億美元"),
        "UNRATE": ("UNRATE", "%"), "SAHMREALTIME": ("SAHMREALTIME", "百分點"),
        "T10Y2Y": ("T10Y2Y", "%"), "DFII10": ("DFII10", "%"), "T5YIE": ("T5YIE", "%"),
        "RETAIL_SALES_MOM": ("RSAFS", "%"),
    }
    for key, (series, unit) in fred_specs.items():
        try:
            if not api_key:
                raise ValueError("未設定 FRED_API_KEY")
            m = None
            if key == "RETAIL_SALES_MOM":
                observations = fred_observations(series, api_key, 4)
                if len(observations) < 2 or month_number(observations[0]["date"])-month_number(observations[1]["date"]) != 1:
                    raise ValueError("RSAFS 最近兩筆不是相鄰月份")
                if observations[1]["value"] <= 0:
                    raise ValueError("RSAFS 前期基數必須大於零")
                m = metric((observations[0]["value"]/observations[1]["value"]-1)*100,
                           observations[0]["date"], unit="%", provider="FRED 官方 API｜RSAFS",
                           source="https://fred.stlouisfed.org/series/RSAFS",
                           method="(本月名目零售額 ÷ 前月 − 1) × 100%",
                           prior_date=observations[1]["date"], prior_value=observations[1]["value"], raw_current=observations[0]["value"])
            else:
                m = fred_metric(series, api_key, unit=unit)
            result[key] = m
        except Exception as exc:
            result[key] = {"value": None, "date": None, "unit": unit, "status": "missing", "error": str(exc),
                           "provider": f"FRED 官方 API｜{series}", "source": f"https://fred.stlouisfed.org/series/{series}"}
    try:
        if not api_key: raise ValueError("未設定 FRED_API_KEY")
        result["NFP_CHANGE"] = nfp_metric(api_key)
    except Exception as exc: result["NFP_CHANGE"] = {"value": None, "date": None, "unit": "千人", "status": "missing", "error": str(exc), "provider": "FRED 官方 API｜PAYEMS", "source": "https://fred.stlouisfed.org/series/PAYEMS"}
    return result


def previous_snapshot(account_id: str, namespace_id: str, token: str) -> dict[str, Any] | None:
    url = f"https://api.cloudflare.com/client/v4/accounts/{quote(account_id)}/storage/kv/namespaces/{quote(namespace_id)}/values/{quote(SNAPSHOT_KEY)}"
    req = Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=20) as response: data = response.read(2_000_001)
    except HTTPError as exc:
        if exc.code == 404: return None
        raise RuntimeError(f"讀取既有快照失敗：HTTP {exc.code}") from exc
    if len(data) > 2_000_000: raise ValueError("既有快照超過 2 MB")
    value = json.loads(data)
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION or not isinstance(value.get("indicators"), dict):
        raise ValueError("既有 KV 快照格式不符；為防覆蓋，停止發布")
    return value


def preserve_previous(current: dict[str, Any], previous: dict[str, Any] | None) -> dict[str, Any]:
    old = (previous or {}).get("indicators", {})
    merged: dict[str, Any] = {}
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    current = dict(current)
    for key in old.keys() - current.keys():
        current[key] = {"value": None, "status": "missing", "error": "本輪未更新此欄位；保留既有觀測"}
    for key, item in current.items():
        if item.get("status") in ("ok", "stale") and valid_number(item.get("value")) and item.get("date"):
            prior = old.get(key)
            if isinstance(prior, dict) and prior.get("date") and prior["date"] > item["date"] and valid_number(prior.get("value")):
                merged[key] = {**prior, "status": "stale", "is_stale": True,
                               "error": "新來源觀測期早於快照，保留較新觀測並標舊"}
            else:
                is_stale = item.get("status") == "stale"
                merged[key] = {**item, "status": "stale" if is_stale else "ok", "is_stale": is_stale}
        else:
            prior = old.get(key)
            if isinstance(prior, dict) and valid_number(prior.get("value")) and prior.get("date"):
                merged[key] = {**prior, "status": "stale", "is_stale": True,
                               "error": item.get("error", "本次抓取失敗；保留前次成功資料")}
            else:
                merged[key] = {**item, "status": "missing", "is_stale": False}
        merged[key]["last_attempt"] = now
        if merged[key].get("status") == "ok":
            merged[key]["last_success"] = now
    return merged


def put_snapshot(account_id: str, namespace_id: str, token: str, snapshot: dict[str, Any]) -> None:
    url = f"https://api.cloudflare.com/client/v4/accounts/{quote(account_id)}/storage/kv/namespaces/{quote(namespace_id)}/values/{quote(SNAPSHOT_KEY)}"
    body = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")).encode()
    req = Request(url, data=body, method="PUT", headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json", "User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as response:
        result = json.loads(response.read(100_001))
    if not result.get("success"):
        raise RuntimeError("Cloudflare KV 未確認寫入成功")


def build_snapshot(api_key: str, previous: dict[str, Any] | None) -> dict[str, Any]:
    indicators = current_metric_set(api_key)
    # These official sources are fetched independently; one failure never drops other rows.
    try:
        indicators["TW_EXPORT_ORDERS"] = taiwan_export_metric(http_text(MOEA_URL))
    except Exception as exc:
        indicators["TW_EXPORT_ORDERS"] = {"value": None, "date": None, "unit": "%", "status": "missing", "error": str(exc), "provider": "經濟部統計處", "source": MOEA_URL}
    try:
        indicators["TW_NDC_SIGNAL"] = fetch_ndc()
    except Exception as exc:
        indicators["TW_NDC_SIGNAL"] = {"value": None, "date": None, "unit": "分", "status": "missing", "error": str(exc), "provider": "國家發展委員會", "source": NDC_URL}
    try:
        payload = http_json(TPEX_URL, headers={"Referer": "https://www.tpex.org.tw/openapi/", "Origin": "https://www.tpex.org.tw"})
        indicators["TPEX_BREADTH"] = tpex_metric(payload)
    except Exception as exc:
        indicators["TPEX_BREADTH"] = {"value": None, "date": None, "unit": "%", "status": "missing", "error": str(exc), "provider": "櫃買中心 TPEx OpenAPI", "source": TPEX_URL}
    freshness_days = {"SOFR": 7, "ON_RRP": 7, "REPO_TEMPORARY_OPERATIONS": 7,
                      "UNRATE": 100, "SAHMREALTIME": 120, "NFP_CHANGE": 100,
                      "T10Y2Y": 7, "DFII10": 7, "T5YIE": 7, "RETAIL_SALES_MOM": 75,
                      "TW_EXPORT_ORDERS": 75, "TW_NDC_SIGNAL": 120, "TPEX_BREADTH": 5}
    today = datetime.now(timezone.utc).date()
    for key, item in indicators.items():
        if item.get("status") == "ok" and item.get("date"):
            try:
                observed = datetime.strptime(item["date"], "%Y-%m-%d").date()
                age_days = (today - observed).days
                if age_days < -1: raise ValueError("觀測日期晚於今日")
                if age_days > freshness_days.get(key, 30):
                    item["status"] = "stale"; item["error"] = f"觀測值已超過 {freshness_days.get(key, 30)} 日有效期"
            except ValueError as exc:
                item.update({"value": None, "date": None, "status": "missing", "error": str(exc)})
    normalized = preserve_previous(indicators, previous)
    good = sum(x.get("status") == "ok" and valid_number(x.get("value")) for x in normalized.values())
    retained = sum(valid_number(x.get("value")) and bool(x.get("date")) for x in normalized.values())
    if retained == 0:
        raise RuntimeError("本次沒有可用新觀測或可保留的舊值；拒絕覆蓋 KV 快照")
    return {"schema_version": SCHEMA_VERSION, "snapshot_key": SNAPSHOT_KEY,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "partial" if any(x.get("status") != "ok" for x in normalized.values()) else "complete",
            "coverage": {"usable": good, "retained": retained, "total": len(normalized)}, "indicators": normalized}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", help="Write diagnostic snapshot JSON locally")
    parser.add_argument("--previous", help="Dry-run only: local prior snapshot JSON")
    args = parser.parse_args()
    if args.previous and not args.dry_run:
        parser.error("--previous 只可搭配 --dry-run；發布必須讀取遠端底本")
    api_key = os.environ.get("FRED_API_KEY", "").strip()
    account = os.environ.get("CF_ACCOUNT_ID", "").strip()
    namespace = os.environ.get("CF_KV_NAMESPACE_ID", "").strip()
    token = os.environ.get("CF_API_TOKEN", "").strip()
    if not args.dry_run and not all((account, namespace, token)):
        raise RuntimeError("發布前缺少 CF_ACCOUNT_ID、CF_KV_NAMESPACE_ID 或 CF_API_TOKEN")
    previous = None if args.dry_run else previous_snapshot(account, namespace, token)
    if args.previous:
        with open(args.previous, encoding="utf-8") as handle:
            previous = json.load(handle)
        if not isinstance(previous, dict) or previous.get("schema_version") != SCHEMA_VERSION or not isinstance(previous.get("indicators"), dict):
            raise ValueError("本地底本結構不符")
    snapshot = build_snapshot(api_key, previous)
    encoded = json.dumps(snapshot, ensure_ascii=False, indent=2)
    print(encoded)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
    if not args.dry_run: put_snapshot(account, namespace, token, snapshot)
    return 0


if __name__ == "__main__":
    try: sys.exit(main())
    except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError) as exc:
        print(f"同步失敗：{exc}", file=sys.stderr); sys.exit(1)
