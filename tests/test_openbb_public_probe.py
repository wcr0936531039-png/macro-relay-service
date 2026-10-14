"""Offline parser contracts; these tests never claim a live connection."""
import unittest
from datetime import date
from integrations.fred_public_probe import parse_csv, probe_batch


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


if __name__ == "__main__":
    unittest.main()
