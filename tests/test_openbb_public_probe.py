"""Offline parser contracts; these tests never claim a live connection."""
import unittest
from datetime import date
from integrations.fred_public_probe import parse_csv, probe_batch, cross_check_common_dates


class PublicProbeTests(unittest.TestCase):
    def test_latest_valid_observation_and_zero(self):
        result = parse_csv("observation_date,DGS10\n2026-10-09,4.2\n2026-10-10,.\n2026-10-11,0\n2026-10-12,NaN\n2026-10-15,5\n", "DGS10", today=date(2026, 10, 14))
        self.assertEqual(result["latest"], {"date": "2026-10-11", "value": 0})
        self.assertEqual(result["rejected_rows"], 3)

    def test_date_column_and_order(self):
        result = parse_csv("DATE,DFII10\n2026-10-13,2.5\n2026-10-12,2.4\n", "DFII10", today=date(2026, 10, 14))
        self.assertEqual(result["latest"]["date"], "2026-10-13")

    def test_wrong_series_column_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_csv("DATE,T10YIE\n2026-10-13,2.4\n", "DGS10")

    def test_duplicate_header_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_csv("DATE,DGS10,DGS10\n2026-10-13,4,5\n", "DGS10")

    def test_conflicting_duplicate_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_csv("DATE,DGS10\n2026-10-13,4\n2026-10-13,5\n", "DGS10", today=date(2026, 10, 14))

    def test_all_missing_never_validates(self):
        with self.assertRaises(ValueError):
            parse_csv("DATE,DGS10\n2026-10-13,.\n", "DGS10", today=date(2026, 10, 14))

    def test_stale_is_not_ok(self):
        result = parse_csv("DATE,DGS10\n2026-09-30,4\n", "DGS10", today=date(2026, 10, 14))
        self.assertEqual(result["status"], "stale")

    def test_selection_checked_before_network(self):
        called = []
        for selection in [[], ["DGS10", "DGS10"], ["DGS10?key=x"]]:
            with self.assertRaises(ValueError):
                probe_batch(selection, lambda s: called.append(s))
        self.assertEqual(called, [])

    def test_source_failures_are_independent(self):
        def fetch(symbol):
            if symbol == "DFII10":
                raise TimeoutError("offline")
            return {"status": "ok"}
        result = probe_batch(["DGS10", "DFII10", "T10YIE"], fetch)
        self.assertEqual(result["validated"], 2)
        self.assertEqual(result["status"], "not_verified")
        self.assertFalse(result["published"])
        self.assertFalse(result["fallback_enabled"])
        self.assertFalse(result["openbb_live_parity_verified"])

    def test_parse_failure_reason_is_retained(self):
        def bad_parse(symbol):
            raise ValueError("official_csv_columns_invalid")
        result = probe_batch(["DGS10"], bad_parse)
        self.assertEqual(result["results"]["DGS10"]["reason"], "official_csv_columns_invalid")


class CommonDateTests(unittest.TestCase):
    def rows(self):
        return {s: {"status": "ok", "unit": "percent", "history": [{"date": "2026-10-09", "value": v}]} for s, v in [("DGS10", 5.24), ("DFII10", 2.91), ("T10YIE", 2.33)]}

    def check(self, rows):
        return cross_check_common_dates(rows, today=date(2026, 10, 14))

    def test_latest_values_are_not_mixed_across_dates(self):
        rows = self.rows()
        rows["T10YIE"]["history"].append({"date": "2026-10-13", "value": 99})
        report = self.check(rows)
        self.assertEqual(report["status"], "verified")
        self.assertEqual(report["as_of"], "2026-10-09")
        self.assertFalse(report["latest_dates_aligned"])
        self.assertFalse(report["independent_source_verified"])
        self.assertEqual(report["score_contribution"], 0)

    def test_no_common_date_never_validates(self):
        rows = self.rows()
        rows["T10YIE"]["history"][0]["date"] = "2026-10-13"
        self.assertEqual(self.check(rows)["reason"], "no_common_observation_dates")

    def test_mismatch_is_exposed_not_repaired(self):
        rows = self.rows()
        rows["T10YIE"]["history"][0]["value"] = 2.5
        report = self.check(rows)
        self.assertEqual(report["status"], "watch")
        self.assertEqual(report["mismatched_dates"], 1)
        self.assertEqual(rows["T10YIE"]["history"][0]["value"], 2.5)

    def test_decimal_rounding_boundary_is_inclusive(self):
        rows = self.rows()
        rows["T10YIE"]["history"][0]["value"] = 2.35
        self.assertEqual(self.check(rows)["status"], "verified")
        rows["T10YIE"]["history"][0]["value"] = 2.351
        self.assertEqual(self.check(rows)["status"], "watch")

    def test_unverified_units_never_validate(self):
        rows = self.rows()
        rows["DFII10"]["unit"] = "basis_points"
        self.assertEqual(self.check(rows)["status"], "unknown")

    def test_future_history_never_validates(self):
        rows = self.rows()
        rows["DGS10"]["history"].append({"date": "2026-10-15", "value": 5})
        self.assertEqual(self.check(rows)["status"], "unknown")

    def test_stale_common_day_never_validates(self):
        rows = self.rows()
        for row in rows.values():
            row["history"][0]["date"] = "2026-10-01"
            row["history"].append({"date": "2026-10-13", "value": 1})
        rows["T10YIE"]["history"][-1]["date"] = "2026-10-12"
        self.assertEqual(self.check(rows)["reason"], "common_observation_date_stale")


if __name__ == "__main__":
    unittest.main()
