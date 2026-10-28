"""Additional read-only contract tests for candidate data shape and error handling."""
import unittest
from integrations.openbb_parity import compare


class CandidateSafetyTests(unittest.TestCase):
    def test_candidate_exception_returns_unknown(self):
        def explode(_):
            raise TimeoutError("network")
        result = compare("DGS10", lambda _: {"status": "ok", "date": "2026-10-10", "value": 4.0}, explode)
        self.assertEqual(result["status"], "unknown")

    def test_candidate_malformed_returns_unknown(self):
        result = compare("DGS10", lambda _: {"status": "ok", "date": "2026-10-10", "value": 4.0}, lambda _: None)
        self.assertEqual(result["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
