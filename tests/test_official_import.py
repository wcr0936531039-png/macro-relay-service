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
