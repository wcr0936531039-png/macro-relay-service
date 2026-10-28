"""Offline preflight readiness checks."""
import tempfile
import unittest
from pathlib import Path
from integrations.openbb_preflight import preflight, REQUIRED


class PreflightTests(unittest.TestCase):
    def test_repository_files_present(self):
        report = preflight()
        self.assertEqual(report["status"], "ready_for_live_validation")
        self.assertFalse(report["candidate_publishing_enabled"])
        self.assertFalse(report["live_parity_verified"])

    def test_missing_files_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = preflight(Path(tmp))
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(set(report["missing_files"]), set(REQUIRED))


if __name__ == "__main__":
    unittest.main()
