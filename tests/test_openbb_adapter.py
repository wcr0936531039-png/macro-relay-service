"""Offline contract tests for the optional OpenBB adapter."""
import sys
import types
import unittest
from unittest.mock import patch
from integrations.openbb_adapter import fetch_fred_series


class FakeFrame:
    empty = False
    columns = ["DGS10"]
    def __init__(self, rows):
        self.rows = rows
    def iterrows(self):
        return iter(self.rows)
    def __getitem__(self, keys):
        return self
    def dropna(self):
        return self
    def sort_index(self):
        self.rows.sort(key=lambda x: x[0])
        return self
    class _Last:
        def __init__(self, rows):
            self.rows = rows
        def iterrows(self):
            return iter(self.rows)
    @property
    def iloc(self):
        class Indexer:
            def __init__(self, rows):
                self.rows = rows
            def __getitem__(self, key):
                return FakeFrame._Last(self.rows[-1:])
        return Indexer(self.rows)


class OpenBBAdapterTests(unittest.TestCase):
    def test_latest_date_not_response_order(self):
        obb = types.SimpleNamespace(fred=types.SimpleNamespace(economy=types.SimpleNamespace(
            fred_series=lambda **kwargs: types.SimpleNamespace(
                to_dataframe=lambda: FakeFrame([("2026-10-10", {"DGS10": 4.1}),
                                         ("2026-10-09", {"DGS10": 4.0})])))))
        with patch.dict(sys.modules, {"openbb": types.SimpleNamespace(obb=obb)}):
            row = fetch_fred_series("DGS10")
        self.assertEqual(row["status"], "ok")
        self.assertEqual(row["date"], "2026-10-10")
        self.assertEqual(row["value"], 4.1)

    def test_invalid_series_id_never_calls_provider(self):
        row = fetch_fred_series("DGS10?inject")
        self.assertEqual(row["status"], "missing")
        self.assertIsNone(row["value"])
        self.assertIn("invalid_series_id", row["error"])

    def test_provider_failure_never_invents_data(self):
        obb = types.SimpleNamespace(fred=types.SimpleNamespace(economy=types.SimpleNamespace(
            fred_series=lambda **kwargs: (_ for _ in ()).throw(RuntimeError("offline")))))
        with patch.dict(sys.modules, {"openbb": types.SimpleNamespace(obb=obb)}):
            row = fetch_fred_series("DGS10")
        self.assertEqual(row["status"], "missing")
        self.assertIsNone(row["value"])
        self.assertIsNone(row["date"])


if __name__ == "__main__":
    unittest.main()
