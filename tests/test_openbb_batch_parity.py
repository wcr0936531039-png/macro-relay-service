"""Offline batch parity contract tests."""
import unittest
from integrations.openbb_batch_parity import check_batch


class BatchParityTests(unittest.TestCase):
    def test_all_match(self):
        official = lambda _: {"status": "ok", "date": "2026-10-10", "value": 4.0}
        candidate = lambda _: {"status": "ok", "date": "2026-10-10", "value": 4.0}
        report = check_batch(["DGS10", "DFII10"], official, candidate)
        self.assertEqual(report["status"], "match")
        self.assertEqual(report["matched"], 2)
        self.assertFalse(report["published"])

    def test_empty_batch_never_passes(self):
        result = check_batch([], lambda _: None)
        self.assertEqual(result["status"], "not_verified")
        self.assertFalse(result["published"])

    def test_duplicate_series_never_passes(self):
        result = check_batch(["DGS10", "DGS10"], lambda _: None)
        self.assertEqual(result["reason"], "empty_or_duplicate_series")
        self.assertEqual(result["matched"], 0)

    def test_partial_failure_never_passes(self):
        official = lambda _: {"status": "ok", "date": "2026-10-10", "value": 4.0}
        def candidate(symbol):
            if symbol == "DFII10":
                raise TimeoutError("offline")
            return {"status": "ok", "date": "2026-10-10", "value": 4.0}
        report = check_batch(["DGS10", "DFII10"], official, candidate)
        self.assertEqual(report["status"], "not_verified")
        self.assertEqual(report["matched"], 1)
        self.assertEqual(report["results"]["DFII10"]["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
