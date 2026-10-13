"""Offline tests for optional source arbitration."""
import unittest
from integrations.openbb_arbitration import choose_observation


class ArbitrationTests(unittest.TestCase):
    def setUp(self):
        self.official = {"status": "ok", "value": 4.0, "date": "2026-10-12", "source": "fred"}
        self.candidate = {"status": "ok", "value": 4.1, "date": "2026-10-13", "source": "openbb:fred"}

    def test_official_wins_even_when_candidate_is_newer(self):
        chosen, reason = choose_observation(self.official, self.candidate, allow_candidate=True)
        self.assertEqual(chosen["source"], "fred")
        self.assertEqual(reason, "official_primary")

    def test_candidate_disabled_by_default(self):
        chosen, reason = choose_observation(None, self.candidate)
        self.assertIsNone(chosen)
        self.assertEqual(reason, "unknown_no_valid_official")

    def test_explicit_fallback(self):
        chosen, reason = choose_observation(None, self.candidate, allow_candidate=True)
        self.assertEqual(chosen["source"], "openbb:fred")
        self.assertEqual(reason, "candidate_fallback")

    def test_invalid_candidate_is_never_promoted(self):
        for value in (None, float("nan"), float("inf"), True):
            candidate = dict(self.candidate, value=value)
            chosen, _ = choose_observation(None, candidate, allow_candidate=True)
            self.assertIsNone(chosen)

    def test_inputs_are_not_mutated(self):
        chosen, _ = choose_observation(self.official, self.candidate)
        chosen["value"] = 99
        self.assertEqual(self.official["value"], 4.0)


if __name__ == "__main__":
    unittest.main()
