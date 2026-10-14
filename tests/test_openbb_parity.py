"""Offline parity contract tests."""
import unittest
from integrations.openbb_parity import compare


class ParityTests(unittest.TestCase):
    def setUp(self):
        self.official = {"status": "ok", "value": 4.2, "date": "2026-10-12"}
        self.candidate = {"status": "ok", "value": 4.2, "date": "2026-10-12"}

    def test_match(self):
        self.assertEqual(compare("DGS10", lambda _: self.official,
                                 lambda _: self.candidate)["status"], "match")

    def test_date_mismatch(self):
        candidate = dict(self.candidate, date="2026-10-11")
        self.assertEqual(compare("DGS10", lambda _: self.official,
                                 lambda _: candidate)["reason"], "observation_date_differs")

    def test_value_mismatch(self):
        candidate = dict(self.candidate, value=4.3)
        self.assertEqual(compare("DGS10", lambda _: self.official,
                                 lambda _: candidate)["reason"], "observation_value_differs")

    def test_official_failure(self):
        def failed(_):
            raise TimeoutError("offline")
        self.assertEqual(compare("DGS10", failed,
                                 lambda _: self.candidate)["status"], "unknown")

    def test_candidate_missing(self):
        candidate = {"status": "missing", "value": None, "date": None}
        self.assertEqual(compare("DGS10", lambda _: self.official,
                                 lambda _: candidate)["reason"], "candidate_unavailable")


if __name__ == "__main__":
    unittest.main()
