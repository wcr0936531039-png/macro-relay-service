"""可轉債官方資料代抓（網站伺服器連不到櫃買／觀測站時用）。不使用任何金鑰。

輸出 data/cb_snapshot.json：
- registries.domestic／overseas：櫃買 OpenAPI bond_ISSBD5_data／bond_ISSBD6_data，只留網站計算用到的欄位，原始回應 SHA-256。
- monthly：櫃買 cbnote 索引列出的最新觀測站月報 CBTRNyyyymm.htm（Big5），解析成 債券代號 → 發行公司、目前轉換價、重設日。
任何一部分這次抓不到，就沿用上次成功的那一份（保留原本的抓取時間；網站超過 36 小時就不用），並在 errors 註明。
不自行推算或補值。
"""
import hashlib
import http.client
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

REGISTRIES = {"domestic": "https://www.tpex.org.tw/openapi/v1/bond_ISSBD5_data",
              "overseas": "https://www.tpex.org.tw/openapi/v1/bond_ISSBD6_data"}
INDEX_URL = "https://www.tpex.org.tw/www/zh-tw/bond/cbnote?response=json"
CBTRN = re.compile(r"^https://mopsov\.twse\.com\.tw/nas/t120/CBTRN(\d{4})(\d{2})\.htm$")
KEEP = ["Date", "IssuerCode", "IssuerName", "BondCode", "ShortName", "Currency", "IssueDate", "MaturityDate", "IssueAmount",
        "OutstandingAmount", "Conversion/ExchangePriceAtIssuance", "Conversion/ExchangePeriodStartDate",
        "Conversion/ExchangePeriodEndDate", "PutOptionDate", "PutOptionPrice"]
UA = "Mozilla/5.0 (compatible; macro-relay-service/1.0; +official public data)"
OUT = Path(__file__).resolve().parents[1] / "data" / "cb_snapshot.json"


def now():
    return datetime.now(timezone.utc).isoformat()


def fetch(url, accept, limit=8_000_000):
    """櫃買回應常傳到一半中斷；同一網址最多試 3 次。"""
    last = None
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent": UA, "Accept": accept}), timeout=40) as r:
                body = r.read(limit + 1)
            if len(body) > limit:
                raise ValueError("response too large")
            return body
        except (http.client.IncompleteRead, TimeoutError, ConnectionError, OSError) as e:
            last = e
            time.sleep(5)
    raise last


def registry_part(kind, body, fetched_at=None):
    rows = json.loads(body.decode("utf-8-sig"))
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{kind}: registry is not a non-empty array")
    if not all(isinstance(r, dict) and "IssuerCode" in r and "BondCode" in r for r in rows):
        raise ValueError(f"{kind}: registry schema changed")
    return {"source_url": REGISTRIES[kind], "fetched_at": fetched_at or now(), "sha256": hashlib.sha256(body).hexdigest(),
            "total_rows": len(rows), "rows": [{k: r.get(k, "") for k in KEEP} for r in rows]}


def latest_monthly(index_body):
    j = json.loads(index_body.decode("utf-8-sig"))
    rows = j.get("tables", [{}])[0].get("data") if str(j.get("stat")).lower() == "ok" else None
    if not isinstance(rows, list):
        raise ValueError("cbnote index schema changed")
    files = []
    for r in rows:
        url = str(r[1] if len(r) > 1 else "").strip()
        m = CBTRN.match(url)
        if m:
            files.append((f"{m[1]}-{m[2]}", url))
    if not files:
        raise ValueError("cbnote index lists no CBTRN file")
    return max(files)


def cell(c):
    return re.sub(r"\s+", " ", re.sub(r"&nbsp;", " ", re.sub(r"<[^>]+>", " ", c))).strip()


def first_line(c):
    return cell(re.split(r"<br\s*/?>", c, flags=re.I)[0])


def roc_slash(v):
    m = re.fullmatch(r"(\d{2,3})/(\d{2})/(\d{2})", v.strip())
    if not m:
        return None
    try:
        return datetime(int(m[1]) + 1911, int(m[2]), int(m[3])).strftime("%Y-%m-%d")
    except ValueError:
        return None


def num(v):
    t = v.replace(",", "").strip()
    try:
        x = float(t)
    except ValueError:
        return None
    return x if x > 0 else None


def parse_monthly(body, month):
    """與網站 parseCbMonthly 同一套規則：資料年月要對、欄名要在、每列 7 欄。"""
    html = body.decode("cp950", "replace")
    ym = re.search(r"資料年月：\s*(?:</b>)?\s*(\d{2,3})年(\d{1,2})月", html)
    file_month = f"{int(ym[1]) + 1911}-{int(ym[2]):02d}" if ym else None
    if file_month != month:
        raise ValueError(f"CBTRN month mismatch: {file_month} vs {month}")
    if "轉(交)換或認股價格(元)" not in html or "重設日期" not in html:
        raise ValueError("CBTRN schema changed")
    prices = {}
    for tr in re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", html, re.I):
        cells = re.findall(r"<td[^>]*>([\s\S]*?)</td>", tr, re.I)
        if len(cells) != 7:
            continue
        issuer, bond = first_line(cells[0]), first_line(cells[1])
        if not re.fullmatch(r"\d{4,6}", issuer) or not re.fullmatch(r"\d{5,7}", bond):
            continue
        prices[bond] = {"issuer": issuer, "price": num(cell(cells[4])), "resetDate": roc_slash(cell(cells[5]))}
    if not prices:
        raise ValueError("CBTRN has no rows")
    return prices


def build(previous=None, fetcher=fetch):
    previous = previous or {}
    out = {"schema_version": 1, "generated_at": now(), "registries": {}, "monthly": None, "errors": []}
    for kind, url in REGISTRIES.items():
        try:
            out["registries"][kind] = registry_part(kind, fetcher(url, "application/json"))
        except Exception as e:  # noqa: BLE001
            out["errors"].append({"part": kind, "error": str(e)[:200]})
            old = (previous.get("registries") or {}).get(kind)
            if old:
                out["registries"][kind] = old
    try:
        month, url = latest_monthly(fetcher(INDEX_URL, "application/json"))
        body = fetcher(url, "text/html")
        out["monthly"] = {"month": month, "source_url": url, "index_url": INDEX_URL, "fetched_at": now(),
                          "sha256": hashlib.sha256(body).hexdigest(), "prices": parse_monthly(body, month)}
    except Exception as e:  # noqa: BLE001
        out["errors"].append({"part": "monthly", "error": str(e)[:200]})
        out["monthly"] = previous.get("monthly")
    return out


def main(path=OUT):
    path = Path(path)
    previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    out = build(previous)
    if not out["registries"] and not out["monthly"]:
        print(json.dumps(out["errors"], ensure_ascii=False))
        raise SystemExit("no CB data available; nothing published")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"registries": {k: v["total_rows"] for k, v in out["registries"].items()},
                      "monthly": (out["monthly"] or {}).get("month"), "errors": out["errors"]}, ensure_ascii=False))


if __name__ == "__main__":
    main(*sys.argv[1:])
