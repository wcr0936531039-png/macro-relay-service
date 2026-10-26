import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_keyless import process_tasks, validate


class ContinueAfterIndicatorFailureTests(unittest.TestCase):
    def test_one_date_mismatch_does_not_stop_later_metrics(self):
        today = datetime.now(timezone.utc).date().isoformat()
        current = {}

        def mismatched_sector():
            raise ValueError("sector date does not match TAIEX")

        def later_metric():
            return {"date": today, "value": 123.0}

        failures = process_tasks(
            [("TWSE_ELECTRONIC", 5, mismatched_sector), ("LATER_METRIC", 5, later_metric)],
            current,
            datetime.now(timezone.utc).isoformat(),
        )

        self.assertEqual([row["id"] for row in failures], ["TWSE_ELECTRONIC"])
        self.assertEqual(current["TWSE_ELECTRONIC"]["status"], "missing")
        self.assertEqual(current["TWSE_ELECTRONIC"]["history"], [])
        self.assertEqual(current["LATER_METRIC"]["status"], "ok")
        self.assertEqual(current["LATER_METRIC"]["history"][-1]["date"], today)

    def test_failed_refresh_preserves_previous_value_as_stale(self):
        today = datetime.now(timezone.utc).date().isoformat()
        prior_point = {"date": today, "value": 42.0}
        current = {"STALE_METRIC": {"history": [prior_point], "status": "stale"}}

        def unavailable():
            raise TimeoutError("upstream timeout")

        failures = process_tasks(
            [("STALE_METRIC", 5, unavailable)],
            current,
            datetime.now(timezone.utc).isoformat(),
        )

        self.assertEqual(len(failures), 1)
        self.assertEqual(current["STALE_METRIC"]["status"], "stale")
        self.assertEqual(current["STALE_METRIC"]["history"], [prior_point])
        self.assertIn("upstream timeout", current["STALE_METRIC"]["error"])


class FutureDatedPolicyRateTests(unittest.TestCase):
    def test_iorb_next_business_day_rate_is_accepted_but_other_series_are_not(self):
        from datetime import timedelta
        ahead = (datetime.now(timezone.utc).date() + timedelta(days=3)).isoformat()
        entry = {"history": [{"date": ahead, "value": 3.9}]}
        self.assertIs(validate(entry, 7, "IORB"), entry)
        with self.assertRaises(ValueError):
            validate(entry, 7, "SOFR")
        far = (datetime.now(timezone.utc).date() + timedelta(days=6)).isoformat()
        with self.assertRaises(ValueError):
            validate({"history": [{"date": far, "value": 3.9}]}, 7, "IORB")


if __name__ == "__main__":
    unittest.main()
