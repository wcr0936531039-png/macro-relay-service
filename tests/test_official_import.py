import datetime as dt
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish_official_import as pub

NOW = dt.datetime(2026, 11, 3, 8, 30, tzinfo=dt.timezone.utc)


def write(folder, name, body):
    (folder / name).write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")


def snapshot(date):
    return {"schema_version": 1, "marketSnapshots": [{"date": date, "rows": [{"id": "2330"}]}]}


class BuildBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = Path(self.tmp.name) / "src"
        self.out = Path(self.tmp.name) / "out"
        self.src.mkdir()
        (self.src / "raw").mkdir()
        write(self.src / "raw", "TWSE.json", {"secret": "raw files are never published"})

    def tearDown(self):
        self.tmp.cleanup()

    def test_publishes_known_parts_with_hashes_and_latest_sessions_only(self):
        write(self.src, "universe.json", {"schema_version": 1, "issuerUniverse": {"rows": []}})
        write(self.src, "series.json", {"schema_version": 1, "series": [{"id": "IORB"}]})
        write(self.src, "cpi.json", {"schema_version": 1, "coreCpiSources": [{"sourceFamily": "FRED"}], "coreCpiFailures": [{"source": "BLS-core-CPI", "error": "403"}]})
        write(self.src, "company.json", {"schema_version": 1, "companies": []})
        write(self.src, "collection-status.json", {"errors": [{"date": "2026-10-31", "error": "holiday"}]})
        for day in ["2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30", "2026-11-02"]:
            write(self.src, day + ".json", snapshot(day))
        manifest = pub.build(self.src, self.out, "afternoon", 5, now=NOW, exits={"official": "1", "sources": "0"})
        names = [p["name"] for p in manifest["parts"]]
        self.assertEqual(names, ["universe.json", "series.json", "cpi.json", "2026-10-27.json", "2026-10-28.json", "2026-10-29.json", "2026-10-30.json", "2026-11-02.json"])
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), sorted(names + ["manifest.json"]))
        for part in manifest["parts"]:
            raw = (self.out / part["name"]).read_bytes()
            self.assertEqual(part["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(part["bytes"], len(raw))
            self.assertEqual(raw, (self.src / part["name"]).read_bytes(), "content is copied unchanged")
        self.assertEqual({p["kind"] for p in manifest["parts"]}, {"universe", "series", "cpi", "market"})
        self.assertEqual(manifest["generatedAt"], "2026-11-03T08:30:00Z")
        self.assertIn({"source": "2026-10-31", "error": "holiday"}, manifest["errors"])
        self.assertIn({"source": "official", "error": "結束碼 1"}, manifest["errors"])
        self.assertFalse(any(e["source"] == "sources" for e in manifest["errors"]))
        saved = json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["schema_version"], 1)
        self.assertEqual(saved["parts"], manifest["parts"])

    def test_malformed_or_oversized_parts_are_not_published_and_are_reported(self):
        write(self.src, "series.json", {"schema_version": 1, "series": []})
        write(self.src, "statistics.json", {"schema_version": 2, "marketStatistics": {}})
        write(self.src, "2026-11-02.json", snapshot("2026-11-01"))
        (self.src / "news.json").write_text("{not json", encoding="utf-8")
        write(self.src, "sources.json", {"schema_version": 1, "researchFeeds": [{"records": ["x" * 4_000_000]}]})
        write(self.src, "universe.json", {"schema_version": 1, "issuerUniverse": {"rows": []}})
        manifest = pub.build(self.src, self.out, None, 5, now=NOW)
        self.assertEqual([p["name"] for p in manifest["parts"]], ["universe.json"])
        reasons = {e["source"]: e["error"] for e in manifest["errors"]}
        self.assertIn("series 是空的", reasons["series.json"])
        self.assertIn("schema_version", reasons["statistics.json"])
        self.assertIn("只含檔名那一天", reasons["2026-11-02.json"])
        self.assertIn("不是 JSON", reasons["news.json"])
        self.assertIn("超過網站單次上限", reasons["sources.json"])
        self.assertFalse((self.out / "series.json").exists())

    def test_failure_only_cpi_and_news_are_not_published(self):
        write(self.src, "series.json", {"schema_version": 1, "series": [{"id": "IORB"}]})
        write(self.src, "cpi.json", {"schema_version": 1, "coreCpiSources": [], "coreCpiFailures": [{"source": "BLS-core-CPI", "error": "403"}]})
        write(self.src, "news.json", {"schema_version": 1, "officialNewsCapture": {"capturedAt": "x", "feeds": [{"topic": "a", "items": [], "error": "timeout"}]}})
        write(self.src, "macro-collection-status.json", {"errors": [{"source": "BLS-core-CPI", "error": "403"}]})
        write(self.src, "cpi-collection-status.json", {"errors": [{"source": "BLS-core-CPI", "error": "403"}]})
        manifest = pub.build(self.src, self.out, None, 5, now=NOW)
        self.assertEqual([p["name"] for p in manifest["parts"]], ["series.json"])
        reasons = {e["source"]: e["error"] for e in manifest["errors"]}
        self.assertIn("只有失敗紀錄", reasons["cpi.json"])
        self.assertIn("全部抓取失敗", reasons["news.json"])
        self.assertEqual(sum(e == {"source": "BLS-core-CPI", "error": "403"} for e in manifest["errors"]), 1, "same failure listed once")

    def test_no_parts_fails_without_publishing(self):
        write(self.src, "macro-collection-status.json", {"errors": [{"source": "IORB", "error": "HTTP 503"}]})
        code = pub.main([str(self.src), str(self.out)])
        self.assertEqual(code, 1)
        manifest = json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["parts"], [])
        self.assertEqual(manifest["errors"], [{"source": "IORB", "error": "HTTP 503"}])

    def test_skipped_statistics_and_news_feed_errors_are_kept(self):
        write(self.src, "series.json", {"schema_version": 1, "series": [{"id": "IORB"}]})
        write(self.src, "macro-collection-status.json", {"errors": [{"source": "TWSE-statistics", "error": "skipped: --skip-statistics"}]})
        write(self.src, "news-collection-status.json", {"feeds": [{"topic": "金管會", "error": "timeout"}, {"topic": "央行", "error": None}]})
        manifest = pub.build(self.src, self.out, "afternoon", 5, now=NOW)
        self.assertIn({"source": "TWSE-statistics", "error": "skipped: --skip-statistics"}, manifest["errors"])
        self.assertIn({"source": "金管會", "error": "timeout"}, manifest["errors"])
        self.assertEqual(len(manifest["errors"]), 2)


def statistics(captured_at, date="2026-11-05"):
    return {"schema_version": 1, "marketStatistics": {"date": date, "capturedAt": captured_at, "margin": {"stat": "OK"}}}


class CreditCaptureWindowTests(unittest.TestCase):
    """GPT 2026-11-06 晨間回報：早上的套件帶了新抓的信用統計，和網站「22:30 前不重抓、保留原觀測日及原核對時間」不符。"""

    MORNING = dt.datetime(2026, 11, 5, 22, 0, tzinfo=dt.timezone.utc)  # 台北 11/06 06:00

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.src, self.out, self.prev = root / "src", root / "out", root / "previous-statistics.json"
        self.src.mkdir()
        write(self.src, "series.json", {"schema_version": 1, "series": [{"id": "IORB"}]})

    def tearDown(self):
        self.tmp.cleanup()

    def test_only_captures_from_2230_to_2359_taipei_are_published(self):
        for captured, ok in [("2026-11-05T14:30:00+00:00", True), ("2026-11-05T15:59:59Z", True), ("2026-11-05T14:29:59+00:00", False),
                             ("2026-11-05T21:26:51.318980+00:00", False), ("2026-11-06T01:50:50.160775+00:00", False), ("2026-11-05T16:00:05+00:00", False), ("2026-11-05T22:40:00", False)]:
            write(self.src, "statistics.json", statistics(captured))
            manifest = pub.build(self.src, self.out, "x", 5, now=self.MORNING)
            names = [p["name"] for p in manifest["parts"]]
            self.assertEqual("statistics.json" in names, ok, captured)
            if not ok:
                reason = {e["source"]: e["error"] for e in manifest["errors"]}["statistics.json"]
                self.assertRegex(reason, "早於 22:30|擷取時間", captured)

    def test_previous_night_capture_is_carried_byte_for_byte(self):
        write(self.src, "macro-collection-status.json", {"errors": [{"source": "TWSE-statistics", "error": "skipped: --skip-statistics"}]})
        self.prev.write_text(json.dumps(statistics("2026-11-05T14:41:07.5+00:00"), ensure_ascii=False, indent=1), encoding="utf-8")
        manifest = pub.build(self.src, self.out, "morning-no-statistics", 5, now=self.MORNING, previous_statistics=self.prev)
        part = next(p for p in manifest["parts"] if p["name"] == "statistics.json")
        self.assertEqual((self.out / "statistics.json").read_bytes(), self.prev.read_bytes(), "原檔不改：保留原觀測日與原核對時間")
        self.assertEqual(part["sha256"], hashlib.sha256(self.prev.read_bytes()).hexdigest())
        self.assertEqual((part["kind"], part["carried"]), ("statistics", True))
        self.assertEqual(manifest["carried"], [{"name": "statistics.json", "date": "2026-11-05", "capturedAt": "2026-11-05T14:41:07.5+00:00"}])
        self.assertNotIn("carryNote", manifest)

    def test_new_night_capture_wins_over_previous(self):
        write(self.src, "statistics.json", statistics("2026-11-06T14:45:00+00:00", "2026-11-06"))
        self.prev.write_text(json.dumps(statistics("2026-11-05T14:41:00+00:00")), encoding="utf-8")
        manifest = pub.build(self.src, self.out, "night", 5, now=dt.datetime(2026, 11, 6, 14, 50, tzinfo=dt.timezone.utc), previous_statistics=self.prev)
        self.assertEqual(json.loads((self.out / "statistics.json").read_text())["marketStatistics"]["date"], "2026-11-06")
        self.assertNotIn("carried", manifest)

    def test_morning_capture_or_old_capture_is_not_carried(self):
        cases = [("2026-11-05T21:26:51+00:00", self.MORNING, "早於 22:30"),
                 ("2026-11-04T14:41:00+00:00", self.MORNING, "超過 30 小時"),
                 ("2026-11-05T14:41:00+00:00", dt.datetime(2026, 11, 5, 14, 0, tzinfo=dt.timezone.utc), "晚於現在")]
        for captured, now, note in cases:
            self.prev.write_text(json.dumps(statistics(captured)), encoding="utf-8")
            manifest = pub.build(self.src, self.out, "morning-no-statistics", 5, now=now, previous_statistics=self.prev)
            self.assertNotIn("statistics.json", [p["name"] for p in manifest["parts"]], captured)
            self.assertFalse((self.out / "statistics.json").exists())
            self.assertIn(note, manifest["carryNote"], captured)
            self.assertNotIn("carried", manifest)
        self.prev.unlink()
        manifest = pub.build(self.src, self.out, "morning-no-statistics", 5, now=self.MORNING, previous_statistics=self.prev)
        self.assertEqual(manifest["carryNote"], "上一份套件沒有信用統計")

    def test_runner_collects_credit_statistics_only_from_2230(self):
        text = (Path(__file__).resolve().parents[1] / "scripts" / "run_official_collector.sh").read_text(encoding="utf-8")
        self.assertIn('[ "$stats" = auto ] && [ "$hm" -lt 2230 ]', text)
        self.assertIn('git show FETCH_HEAD:statistics.json > "$previous"', text)
        self.assertIn('--previous-statistics "$previous"', text)


class EveningScheduleTests(unittest.TestCase):
    """擁有者 2026-11-13 00:01：晚上 22:30 巡檢前要有當天行情與 6 小時內的產業來源，下午到傍晚多排三次。"""

    def test_evening_runs_are_scheduled_on_weekdays(self):
        text = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "official_collector.yml").read_text(encoding="utf-8")
        for cron in ("'50 6 * * 1-5'", "'50 8 * * 1-5'", "'50 10 * * 1-5'", "'20 8 * * 1-5'", "'55 21 * * *'", "'40 14 * * 1-5'"):
            self.assertIn("- cron: " + cron, text)
        self.assertIn("cancel-in-progress: false", text)


class CollectorRetryTests(unittest.TestCase):
    """擁有者 2026-11-05 21:54「好」：下載中斷（IncompleteRead、連線被重設）最多 4 次、間隔 5／10／20 秒；逾時與 HTTP 錯誤照舊 2 次、不等待。"""

    def setUp(self):
        import http.client
        import types
        import urllib.error
        import urllib.parse
        import urllib.request
        src = (Path(__file__).resolve().parents[1] / "vendor" / "site-collector" / "scripts" / "collect-official-data.py").read_text(encoding="utf-8")
        self.code = src[src.index("RETRY_WAITS = "):src.index("def save(")]
        self.mods = types.SimpleNamespace(http=http, urllib=urllib, types=types)
        self.inc = http.client.IncompleteRead(b"x" * 10, 5)

    def run_fetch(self, outcomes, url="https://openapi.twse.com.tw/v1/opendata/t187ap03_L"):
        sleeps, agents, it = [], [], iter(outcomes)

        class Body:
            def __init__(self, data):
                self.data = data

            def read(self):
                return self.data

        def fake_open(request, timeout):
            agents.append(request.get_header("User-agent"))
            item = next(it)
            if isinstance(item, BaseException):
                raise item
            return Body(item)

        urllib = self.mods.types.SimpleNamespace(parse=self.mods.urllib.parse, request=self.mods.types.SimpleNamespace(Request=self.mods.urllib.request.Request, urlopen=fake_open))
        ns = {"urllib": urllib, "http": self.mods.http, "time": self.mods.types.SimpleNamespace(sleep=sleeps.append)}
        exec(self.code, ns)
        try:
            return ns["fetch"](url), sleeps, agents
        except Exception as exc:  # noqa: BLE001
            return type(exc).__name__, sleeps, agents

    def test_broken_download_is_retried_with_waits(self):
        self.assertEqual(self.run_fetch([self.inc, self.inc, b"ok"])[:2], ("ok", [5, 10]))
        result, sleeps, agents = self.run_fetch([self.inc] * 4)
        self.assertEqual((result, sleeps, len(agents)), ("IncompleteRead", [5, 10, 20], 4))
        self.assertEqual(self.run_fetch([self.mods.urllib.error.URLError(ConnectionResetError()), b"ok"])[:2], ("ok", [5]))

    def test_timeouts_and_http_errors_keep_two_quick_attempts(self):
        result, sleeps, agents = self.run_fetch([TimeoutError(), TimeoutError(), b"never"])
        self.assertEqual((result, sleeps, len(agents)), ("TimeoutError", [], 2))
        result, sleeps, agents = self.run_fetch([self.mods.urllib.error.HTTPError("u", 404, "nf", {}, None)] * 2 + [b"never"])
        self.assertEqual((result, sleeps, len(agents)), ("HTTPError", [], 2))

    def test_fred_alternates_default_and_named_user_agent(self):
        result, _, agents = self.run_fetch([self.inc, self.inc, self.inc, b"ok"], "https://fred.stlouisfed.org/graph/fredgraph.csv?id=IORB")
        self.assertEqual(result, "ok")
        self.assertEqual(agents, [None, "TaiwanStockMaster/1.0", None, "TaiwanStockMaster/1.0"])
        self.assertEqual(self.run_fetch([b"ok"])[2], ["TaiwanStockMaster/1.0"], "other sites keep the named agent")


class VendoredCollectorTests(unittest.TestCase):
    def test_vendored_site_collector_files_exist_and_carry_no_credentials(self):
        root = Path(__file__).resolve().parents[1] / "vendor" / "site-collector"
        files = ["scripts/collect-official-data.py", "scripts/collect-source-research.mjs", "worker/source-research.js", "worker/official-news.js"]
        for name in files:
            text = (root / name).read_text(encoding="utf-8")
            for word in ["Bearer ", "OAI-Sites-Authorization", "TIINGO", "api_key="]:
                self.assertNotIn(word, text, f"{name} must not reference {word}")


if __name__ == "__main__":
    unittest.main()
