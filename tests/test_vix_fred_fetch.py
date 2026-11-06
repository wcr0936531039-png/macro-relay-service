"""擁有者 2026-11-06 17:27「好」：VIX 先用 Cboe 官方每日收盤（比 FRED 快約一天），FRED 當備援；
抓 FRED 先用 Python 預設 User-Agent（GitHub 上 FRED 會擋自訂字串），下載中斷多試幾次。"""
import sys
import unittest
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sync_keyless as keyless  # noqa: E402
import sync_cross_market as cross  # noqa: E402

FIXTURE = (ROOT / "tests" / "fixtures" / "cboe_vix_history_tail_20261106.csv").read_text(encoding="utf-8")


class Body:
    def __init__(self, data):
        self.data = data

    def read(self, limit=-1):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeNet:
    def __init__(self, outcomes):
        self.outcomes, self.agents, self.urls = list(outcomes), [], []

    def __call__(self, request, timeout=None):
        self.agents.append(request.get_header("User-agent"))
        self.urls.append(request.full_url)
        item = self.outcomes.pop(0)
        if isinstance(item, BaseException):
            raise item
        return Body(item)


class CboeVixTests(unittest.TestCase):
    def test_parses_official_daily_close(self):
        entry = keyless.cboe_vix_history(FIXTURE)
        self.assertEqual(entry["history"][-1], {"date": "2026-11-05", "value": 28.18})
        self.assertEqual(entry["history"][-2], {"date": "2026-11-04", "value": 16.61}, "same closes FRED republishes")
        self.assertEqual(len(entry["history"]), 20)
        self.assertEqual(entry["source"], keyless.CBOE_VIX_URL)
        self.assertIn("高 28.36", entry["method"])

    def test_rejects_wrong_header_or_too_little_history(self):
        with self.assertRaises(ValueError):
            keyless.cboe_vix_history("Date,Close\n11/05/2026,28.18\n")
        with self.assertRaises(ValueError):
            keyless.cboe_vix_history("\n".join(FIXTURE.splitlines()[:4]))

    def test_impossible_rows_are_skipped_not_used(self):
        bad = FIXTURE.rstrip("\n") + "\n11/06/2026,20,19,21,25\n"
        self.assertEqual(keyless.cboe_vix_history(bad)["history"][-1]["date"], "2026-11-05", "low>high row is ignored")

    def test_falls_back_to_fred_when_cboe_fails(self):
        old_cboe, old_fred = keyless.cboe_vix_history, keyless.fred_csv
        try:
            keyless.cboe_vix_history = lambda: (_ for _ in ()).throw(ValueError("Cboe VIX CSV header mismatch"))
            keyless.fred_csv = lambda sid: {"history": [{"date": "2026-11-04", "value": 16.61}], "source": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS", "provider": "FRED 官方公開 CSV｜VIXCLS"}
            entry = keyless.vix_metric()
            self.assertEqual(entry["provider"], "FRED 官方公開 CSV｜VIXCLS")
            self.assertIn("改用 FRED", entry["method"])
        finally:
            keyless.cboe_vix_history, keyless.fred_csv = old_cboe, old_fred


class FetchPublicTests(unittest.TestCase):
    def setUp(self):
        self.old_open, self.old_sleep, self.sleeps = keyless.urlopen, keyless.time.sleep, []
        keyless.time.sleep = self.sleeps.append

    def tearDown(self):
        keyless.urlopen, keyless.time.sleep = self.old_open, self.old_sleep

    def test_fred_tries_python_default_agent_first(self):
        net = FakeNet([TimeoutError(), b"ok"])
        keyless.urlopen = net
        self.assertEqual(keyless.fetch_public("https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS", "text/csv", 100, prefer_default_agent=True), b"ok")
        self.assertEqual(net.agents, [None, keyless.legacy.USER_AGENT])
        self.assertEqual(self.sleeps, [])

    def test_broken_download_retried_four_times_with_waits(self):
        import http.client
        broken = http.client.IncompleteRead(b"x", 5)
        net = FakeNet([broken, broken, broken, b"ok"])
        keyless.urlopen = net
        self.assertEqual(keyless.fetch_public(keyless.CBOE_VIX_URL, "text/csv", 100), b"ok")
        self.assertEqual(self.sleeps, [5, 10, 20])
        self.assertEqual(net.agents[0], keyless.legacy.USER_AGENT, "other sites keep the named agent first")

    def test_http_errors_stop_after_two_quick_attempts(self):
        net = FakeNet([urllib.error.HTTPError("u", 403, "no", {}, None)] * 3)
        keyless.urlopen = net
        with self.assertRaises(urllib.error.HTTPError):
            keyless.fetch_public(keyless.CBOE_VIX_URL, "text/csv", 100)
        self.assertEqual((len(net.agents), self.sleeps), (2, []))

    def test_oversized_response_is_rejected(self):
        keyless.urlopen = FakeNet([b"x" * 101])
        with self.assertRaises(ValueError):
            keyless.fetch_public(keyless.CBOE_VIX_URL, "text/csv", 100)


class CrossMarketFredAgentTests(unittest.TestCase):
    def test_fred_first_attempt_uses_default_agent(self):
        old_open, old_sleep = cross.urlopen, cross.time.sleep
        try:
            net = FakeNet([TimeoutError(), b"observation_date,SP500\n"])
            cross.urlopen, cross.time.sleep = net, (lambda s: None)
            self.assertEqual(cross.fetch_text("https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500"), "observation_date,SP500\n")
            self.assertEqual(net.agents, [None, cross.UA])
            net = FakeNet([b"{}"])
            cross.urlopen = net
            cross.fetch_text("https://www.twse.com.tw/x")
            self.assertEqual(net.agents, [cross.UA], "non-FRED unchanged")
        finally:
            cross.urlopen, cross.time.sleep = old_open, old_sleep


if __name__ == "__main__":
    unittest.main()
