"""Additional parity validation regressions. No network or publishing."""
import unittest

from integrations.openbb_parity import compare


class ParityValidationTests(unittest.TestCase):
    def setUp(self):
        self.official = lambda _: {"status": "ok", "date": "2026-10-10", "value": 4.1}

    def test_bad_numeric_candidate_returns_unknown(self):
        result = compare("DGS10", self.official, lambda _: {
            "status": "ok", "date": "2026-10-10", "value": "not-a-number"})
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["reason"], "candidate_invalid_observation")

    def test_candidate_future_date_returns_unknown(self):
        result = compare("DGS10", self.official, lambda _: {
            "status": "ok", "date": "2099-01-01", "value": 4.1})
        self.assertEqual(result["status"], "unknown")

    def test_candidate_nan_returns_unknown(self):
        result = compare("DGS10", self.official, lambda _: {
            "status": "ok", "date": "2026-10-10", "value": float("nan")})
        self.assertEqual(result["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
