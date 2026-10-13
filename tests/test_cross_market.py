import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("cross", Path(__file__).resolve().parents[1] / "scripts/sync_cross_market.py")
cross = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cross)


class HistoryContractTests(unittest.TestCase):
    def test_iso_date_and_valid_zero(self):
        self.assertEqual(cross.iso_date("115/10/13"), "2026-10-13")
        self.assertIsNone(cross.iso_date("2026-02-30"))
        self.assertEqual(cross.number("0"), 0)
        self.assertIsNone(cross.number(None))
        self.assertIsNone(cross.number(float("nan")))

    def test_twse_column_mapping_and_units(self):
        row = cross.twse_month({"stat": "OK", "fields": ["日期", "成交金額", "發行量加權股價指數"], "data": [["115/10/13", "100,000,000", "48,000.00"]]}, "https://www.twse.com.tw/test")[0]
        self.assertEqual(row["value"], 48000)
        self.assertEqual(row["totalValueTwd"], 100000000)
        self.assertEqual(row["available_at"], "2026-10-13T05:30:00+00:00")

    def test_funding_zero_and_date_mismatch(self):
        body = {"stat": "OK", "date": "20261013", "fields": ["單位名稱", "買進金額", "賣出金額", "買賣差額"], "data": [["外資及陸資（不含外資自營商）", "0", "0", "0"], ["投信", "0", "1,000", "-1,000"]]}
        result = cross.institution_flows(body, "2026-10-13")
        self.assertEqual(result["foreignNetTwd"], 0)
        self.assertEqual(result["investmentTrustNetTwd"], -1000)
        with self.assertRaises(ValueError):
            cross.institution_flows(body, "2026-10-12")

    def test_non_day_trade_uses_amounts_not_volume_percentage(self):
        body = {"stat": "OK", "date": "20261013", "tables": [{"fields": ["當日沖銷交易總成交股數占市場比重", "當日沖銷交易總買進成交金額", "當日沖銷交易總賣出成交金額"], "data": [["90", "200", "400"]]}]}
        self.assertEqual(cross.daytrade_value(body, "2026-10-13")["dayTradeValueTwd"], 300)
        body["tables"][0]["fields"] = ["股數占市場比重"]
        with self.assertRaises(ValueError):
            cross.daytrade_value(body, "2026-10-13")

    def test_incomplete_yahoo_session_and_null_are_not_closes(self):
        stamps = [int(datetime(2026, 10, d, 13, 30, tzinfo=timezone.utc).timestamp()) for d in (12, 13)]
        payload = {"chart": {"result": [{"meta": {"symbol": "^SOX", "exchangeTimezoneName": "America/New_York"}, "timestamp": stamps, "indicators": {"quote": [{"close": [100, 110]}]}}]}}
        with patch.object(cross, "NOW", datetime(2026, 10, 13, 19, 0, tzinfo=timezone.utc)):
            rows = cross.parse_sox_yahoo(payload, "https://query1.finance.yahoo.com/test")["history"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date"], "2026-10-12")
        payload["chart"]["result"][0]["meta"]["symbol"] = "SOXX"
        with self.assertRaises(ValueError):
            cross.parse_sox_yahoo(payload, "https://query1.finance.yahoo.com/test")

    def test_conflicting_duplicate_prices_rejected(self):
        point = {"date": "2026-09-01", "value": 100, "available_at": "2026-09-01T05:30:00+00:00"}
        with self.assertRaises(ValueError):
            cross.unique_points([point, {**point, "value": 101}])


if __name__ == "__main__":
    unittest.main()
