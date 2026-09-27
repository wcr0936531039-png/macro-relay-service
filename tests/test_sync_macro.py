import sys
import unittest
import json
import subprocess
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sync_macro as relay


class RelayValidationTests(unittest.TestCase):
    def test_zero_is_a_valid_observation(self):
        self.assertTrue(relay.valid_number(0))
        self.assertTrue(relay.valid_number("0"))
        self.assertFalse(relay.valid_number("."))
        self.assertFalse(relay.valid_number(""))
        self.assertFalse(relay.valid_number(None))

    def test_fred_observations_keep_zero_and_drop_dot(self):
        original = relay.http_json
        try:
            relay.http_json = lambda _url: {"observations": [
                {"date": "2026-09-25", "value": "0"},
                {"date": "2026-09-24", "value": "."},
            ]}
            rows = relay.fred_observations("RRPONTSYD", "test", 2)
            self.assertEqual(rows, [{"date": "2026-09-25", "value": 0.0}])
        finally:
            relay.http_json = original

    def test_nfp_only_uses_adjacent_months_and_excludes_dot(self):
        original = relay.fred_observations
        try:
            relay.fred_observations = lambda _series, _key, _limit: [
                {"date": "2026-08-01", "value": 160000.0},
                {"date": "2026-07-01", "value": 159850.0},
            ]
            row = relay.nfp_metric("test")
            self.assertEqual(row["value"], 150.0)
            self.assertEqual(row["date"], "2026-08-01")
        finally:
            relay.fred_observations = original
        self.assertEqual(relay.month_number("2026-08-01") - relay.month_number("2026-07-01"), 1)
        self.assertEqual(relay.month_number("2026-08-01") - relay.month_number("2026-06-01"), 2)

    def test_ndc_light_mapping(self):
        row = relay.ndc_metric({"line": [{"x": "202608", "y": 41}]})
        self.assertEqual(row["date"], "2026-08-01")
        self.assertEqual(row["light"], "紅燈")

    def test_tpex_date_and_zero_advancers(self):
        row = relay.tpex_metric([{"Date": "1150925", "PriceRiseCompanyNumbers": 0,
                                  "PriceDeclineCompanyNumbers": 10}])
        self.assertEqual(row["date"], "2026-09-25")
        self.assertEqual(row["value"], 0.0)

    def test_moea_uses_usd_monthly_yoy_not_cumulative_or_twd_yoy(self):
        html = """<table><tr><td>115年</td><td>1-8月</td><td>704 990</td><td>55.03</td><td>223 936</td><td>57.59</td></tr>
        <tr><td></td><td>7月</td><td>97 939</td><td>61.85</td><td>31 543</td><td>77.77</td></tr>
        <tr><td></td><td>8月</td><td>102 955</td><td>71.35</td><td>32 982</td><td>81.89</td></tr></table>"""
        row = relay.taiwan_export_metric(html)
        self.assertEqual(row["date"], "2026-08-01")
        self.assertEqual(row["value"], 71.35)

    def test_failed_fetch_preserves_previous_as_stale(self):
        old = {"schema_version": 1, "indicators": {"SOFR": {"value": 4.1, "date": "2026-09-25", "status": "ok"}}}
        merged = relay.preserve_previous({"SOFR": {"value": None, "date": None, "status": "missing", "error": "upstream error"}}, old)
        self.assertEqual(merged["SOFR"]["value"], 4.1)
        self.assertEqual(merged["SOFR"]["status"], "stale")
        self.assertTrue(merged["SOFR"]["is_stale"])

    def test_rejects_backwards_observation(self):
        old = {"schema_version": 1, "indicators": {"UNRATE": {"value": 4.2, "date": "2026-08-01", "status": "ok"}}}
        new = {"UNRATE": {"value": 4.1, "date": "2026-07-01", "status": "ok"}}
        merged = relay.preserve_previous(new, old)
        self.assertEqual(merged["UNRATE"]["value"], 4.2)
        self.assertEqual(merged["UNRATE"]["status"], "stale")


    def test_producer_reader_retail_contract(self):
        with patch.object(relay, "fred_observations", return_value=[
            {"date": "2026-08-01", "value": 102},
            {"date": "2026-07-01", "value": 100},
        ]):
            indicators = relay.current_metric_set("test")
        self.assertAlmostEqual(indicators["RETAIL_SALES_MOM"]["value"], 2)
        script = "import {adaptSnapshotRows} from './worker/read_macro_snapshot.js'; let s=''; for await(const c of process.stdin)s+=c; console.log(JSON.stringify(adaptSnapshotRows(JSON.parse(s))));"
        result = subprocess.run(["node", "--input-type=module", "-e", script],
            cwd=Path(__file__).resolve().parents[1], input=json.dumps({"schema_version": 1, "indicators": indicators}),
            capture_output=True, text=True, check=True)
        row = next(x for x in json.loads(result.stdout) if x["id"] == "RETAIL_SALES_MOM")
        self.assertAlmostEqual(row["value"], 2)

    def test_retail_gap_and_zero_denominator_fail_closed(self):
        for previous in [{"date": "2026-06-01", "value": 100}, {"date": "2026-07-01", "value": 0}]:
            with patch.object(relay, "fred_observations", return_value=[{"date": "2026-08-01", "value": 102}, previous]):
                row = relay.current_metric_set("test")["RETAIL_SALES_MOM"]
                self.assertEqual(row["status"], "missing")

    def test_omitted_metric_is_preserved_with_attempt_timestamp(self):
        old = {"indicators": {"ON_RRP": {"value": 0, "date": "2026-09-25", "last_success": "original"}}}
        row = relay.preserve_previous({}, old)["ON_RRP"]
        self.assertEqual(row["value"], 0)
        self.assertEqual(row["last_success"], "original")
        self.assertTrue(row["last_attempt"])
        self.assertTrue(row["is_stale"])

    def test_dry_run_never_accesses_cloudflare(self):
        with patch.object(sys, "argv", ["sync_macro.py", "--dry-run"]), \
             patch.object(relay, "previous_snapshot") as read, \
             patch.object(relay, "put_snapshot") as write, \
             patch.object(relay, "build_snapshot", return_value={"status": "partial"}), \
             redirect_stdout(StringIO()):
            self.assertEqual(relay.main(), 0)
            read.assert_not_called()
            write.assert_not_called()


    def test_ndc_news_uses_observation_month(self):
        row = relay.ndc_news_metric("<p>發布日期：115年8月27日</p><p>115年7月景氣對策信號綜合判斷分數為41分，與上月持平。</p>", "https://www.ndc.gov.tw/test")
        self.assertEqual(row["date"], "2026-07-01")
        self.assertEqual(row["value"], 41)
        self.assertEqual(row["light"], "紅燈")
        with self.assertRaises(ValueError):
            relay.ndc_news_metric("<h1>Access denied</h1>", "https://www.ndc.gov.tw/test")

    def test_ndc_news_fallback_discovers_latest_release(self):
        listing = '<a href="/old">115年6月份景氣概況新聞稿</a><a href="/latest">115年7月份景氣概況新聞稿</a>'
        article = '<p>115年7月景氣對策信號綜合判斷分數為41分</p>'
        with patch.object(relay, "http_json", side_effect=ValueError("403")), patch.object(relay, "http_text", side_effect=[listing, article]):
            row = relay.fetch_ndc()
        self.assertEqual(row["source"], "https://www.ndc.gov.tw/latest")
        self.assertIn("403", row["upstream_warning"])


if __name__ == "__main__":
    unittest.main()
