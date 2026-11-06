#!/usr/bin/env python3
"""把官方資料收集程式的輸出整理成網站匯入用的套件（清單 manifest.json＋各部分檔）。

用法：python scripts/publish_official_import.py <收集輸出資料夾> <套件輸出資料夾> [--window 標籤] [--keep-sessions 5]

- 只複製網站認得的部分檔：universe.json、YYYY-MM-DD.json（行情）、series.json、statistics.json、cpi.json、
  sources.json、news.json。raw/、狀態檔、company.json 都不發布。
- 每個部分檔先檢查格式（schema_version 1 與該類別的主欄位）；不符就不發布、記進 errors，不修改內容、不補值。
- 清單記錄每個檔的類別、位元組數與 SHA-256（網站讀到的內容雜湊不符就不匯入）。
- 收集端失敗（狀態檔的 errors、收集程式結束碼）照實寫進 errors；一個部分檔都沒有就失敗結束，不發布空套件。
- 這裡不連網站、不需要任何金鑰；GitHub 工作流程把套件強制推到 official-import 分支（只保留最新一份）。
- 信用統計（2026-11-06 GPT 晨間回報的缺口）：和網站同一條規則，只發布台北 22:30～23:59 擷取的那份；
  其他時間的擷取不發布。這次沒有新的夜間信用統計時，沿用上一份套件裡的夜間信用統計（原檔一個位元組都不改，
  保留原觀測日與原核對時間），超過 30 小時就不再沿用（網站 36 小時後不收，留時間給巡檢延後）。
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

FIXED = {
    "universe.json": ("universe", "issuerUniverse"),
    "series.json": ("series", "series"),
    "statistics.json": ("statistics", "marketStatistics"),
    "cpi.json": ("cpi", "coreCpiSources"),
    "sources.json": ("sources", "researchFeeds"),
    "news.json": ("news", "officialNewsCapture"),
}
MARKET = re.compile(r"^\d{4}-\d{2}-\d{2}\.json$")
MAX_PART_BYTES = 3_900_000
TPE = dt.timezone(dt.timedelta(hours=8))
CREDIT_CAPTURE_FROM = (22, 30)  # 網站 taiwanCreditCaptureAllowed：台北時間 22:30 起才抓信用統計
CARRY_MAX_HOURS = 30
STATUS_FILES = [
    "collection-status.json",
    "macro-collection-status.json",
    "cpi-collection-status.json",
    "statistics-collection-status.json",
    "source-collection-status.json",
    "news-collection-status.json",
]


def credit_captured_at(data):
    stats = data.get("marketStatistics") if isinstance(data, dict) else None
    try:
        captured = dt.datetime.fromisoformat(str((stats or {}).get("capturedAt")).replace("Z", "+00:00"))
    except ValueError:
        return None
    return captured if captured.tzinfo else None


def credit_capture_problem(data):
    captured = credit_captured_at(data)
    if not captured:
        return "信用統計沒有可辨識的擷取時間（需含時區）"
    local = captured.astimezone(TPE)
    if (local.hour, local.minute) < CREDIT_CAPTURE_FROM:
        return f"信用統計擷取於台北 {local:%m/%d %H:%M}，早於 22:30（網站規則：22:30 前不重抓信用統計，保留原觀測日及原核對時間）"
    return None


def check_part(name, data):
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        return "schema_version 不是 1"
    if MARKET.match(name):
        snaps = data.get("marketSnapshots")
        if not isinstance(snaps, list) or len(snaps) != 1 or not isinstance(snaps[0], dict) or str(snaps[0].get("date")) + ".json" != name:
            return "行情檔應只含檔名那一天"
        return None
    key = FIXED[name][1]
    if key not in data:
        return f"缺少 {key}"
    if key in ("series", "researchFeeds") and not (isinstance(data[key], list) and data[key]):
        return f"{key} 是空的"
    # 只有失敗紀錄的 CPI／新聞不發布：網站會保留自己已有的資料並自己重抓，不讓空結果蓋掉。
    if key == "coreCpiSources" and not (isinstance(data[key], list) and data[key]):
        return "核心 CPI 沒有任何可用來源（只有失敗紀錄）"
    if key == "officialNewsCapture" and not any(isinstance(f, dict) and f.get("items") for f in (data[key] or {}).get("feeds") or []):
        return "官方新聞全部抓取失敗"
    if key == "marketStatistics":
        return credit_capture_problem(data)
    return None


def carry_statistics(path, now):
    """沿用上一份套件的夜間信用統計。回傳 (原始位元組, 說明) 或 (None, 不沿用的原因)。"""
    path = Path(path)
    if not path.exists() or not path.stat().st_size:
        return None, "上一份套件沒有信用統計"
    raw = path.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"))
        problem = check_part("statistics.json", data)
    except (ValueError, AttributeError, TypeError):
        return None, "上一份信用統計不是 JSON"
    if problem:
        return None, "上一份" + problem
    captured = credit_captured_at(data)
    age = (now - captured).total_seconds() / 3600
    if age < 0:
        return None, "上一份信用統計的擷取時間晚於現在"
    if age > CARRY_MAX_HOURS:
        return None, f"上一份信用統計擷取於 {age:.0f} 小時前，超過 {CARRY_MAX_HOURS} 小時不再沿用"
    stats = data["marketStatistics"]
    return raw, {"name": "statistics.json", "date": stats.get("date"), "capturedAt": stats.get("capturedAt")}


def collector_errors(src, exits):
    errors = []
    for status in STATUS_FILES:
        path = src / status
        if not path.exists():
            continue
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            errors.append({"source": status, "error": "狀態檔不是 JSON"})
            continue
        for row in body.get("errors") or []:
            if isinstance(row, dict):
                errors.append({"source": str(row.get("source") or row.get("date") or row.get("key") or status)[:120], "error": str(row.get("error"))[:300]})
        if status == "statistics-collection-status.json" and body.get("error"):
            errors.append({"source": "TWSE-statistics", "error": str(body["error"])[:300]})
        for feed in body.get("feeds") or []:
            if isinstance(feed, dict) and feed.get("error"):
                errors.append({"source": str(feed.get("topic") or feed.get("source"))[:120], "error": str(feed["error"])[:300]})
    for name, code in exits.items():
        if code not in ("", "0", None):
            errors.append({"source": name, "error": f"結束碼 {code}"})
    unique = []
    for row in errors:
        if row not in unique:
            unique.append(row)
    return unique


def build(src, out, window=None, keep_sessions=5, now=None, collector=None, exits=None, previous_statistics=None):
    src, out = Path(src), Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    now = now or dt.datetime.now(dt.timezone.utc)
    parts, errors = [], []
    markets = sorted(p.name for p in src.glob("*.json") if MARKET.match(p.name))[-keep_sessions:] if keep_sessions else []
    for name in [n for n in FIXED if (src / n).exists()] + markets:
        raw = (src / name).read_bytes()
        try:
            problem = check_part(name, json.loads(raw.decode("utf-8")))
        except (ValueError, AttributeError, TypeError):
            problem = "不是 JSON"
        if not problem and len(raw) > MAX_PART_BYTES:
            problem = f"{len(raw)} 位元組，超過網站單次上限"
        if problem:
            errors.append({"source": name, "error": "未發布：" + str(problem)})
            continue
        (out / name).write_bytes(raw)
        parts.append({"name": name, "kind": "market" if MARKET.match(name) else FIXED[name][0], "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    carried, carry_note = [], None
    if previous_statistics and not any(p["name"] == "statistics.json" for p in parts):
        raw, note = carry_statistics(previous_statistics, now)
        if raw:
            (out / "statistics.json").write_bytes(raw)
            parts.append({"name": "statistics.json", "kind": "statistics", "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "carried": True})
            carried.append(note)
        else:
            carry_note = note
    errors = collector_errors(src, exits or {}) + errors
    manifest = {
        "schema_version": 1,
        "generatedAt": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "window": window,
        "collector": collector or {},
        "parts": parts,
        "errors": errors[:50],
    }
    if carried:
        manifest["carried"] = carried
    if carry_note:
        manifest["carryNote"] = carry_note
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--window")
    ap.add_argument("--keep-sessions", type=int, default=5)
    ap.add_argument("--exit", action="append", default=[], help="名稱=結束碼，例如 official=0")
    ap.add_argument("--previous-statistics", help="上一份套件的 statistics.json；這次沒有新的夜間信用統計時沿用")
    args = ap.parse_args(argv)
    collector = {k: v for k, v in {"repo": os.environ.get("GITHUB_REPOSITORY"), "commit": os.environ.get("GITHUB_SHA"), "run": os.environ.get("GITHUB_RUN_ID"), "siteCollector": "v253"}.items() if v}
    exits = dict(item.split("=", 1) for item in args.exit if "=" in item)
    manifest = build(args.src, args.out, args.window, args.keep_sessions, collector=collector, exits=exits, previous_statistics=args.previous_statistics)
    print(json.dumps({"parts": [(p["name"], p["bytes"]) for p in manifest["parts"]], "carried": manifest.get("carried"), "carryNote": manifest.get("carryNote"), "errors": manifest["errors"]}, ensure_ascii=False))
    if not manifest["parts"]:
        print("NO_PARTS: 沒有可發布的部分檔，保留上一份套件", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
