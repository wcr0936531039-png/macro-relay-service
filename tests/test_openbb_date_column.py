"""Read-only checks for a provider dataframe with an explicit date column.

This is a regression contract for an alternate OpenBB response shape.
"""
import sys
import types
import unittest
from unittest.mock import patch

from integrations.openbb_adapter import fetch_fred_series


class ExplicitDateFrame:
    empty = False
    columns = ["date", "value"]
    def __init__(self):
        self.rows = [
            {"date": "2026-10-09", "value": 4.0},
            {"date": "2026-10-10", "value": 4.1},
        ]


class DateColumnTests(unittest.TestCase):
    def test_explicit_date_column(self):
        obb = types.SimpleNamespace(fred=types.SimpleNamespace(economy=types.SimpleNamespace(
            fred_series=lambda **kwargs: types.SimpleNamespace(
                to_dataframe=lambda: ExplicitDateFrame()))))
        with patch.dict(sys.modules, {"openbb": types.SimpleNamespace(obb=obb)}):
            result = fetch_fred_series("DGS10")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["date"], "2026-10-10")
        self.assertEqual(result["value"], 4.1)


if __name__ == "__main__":
    unittest.main()
