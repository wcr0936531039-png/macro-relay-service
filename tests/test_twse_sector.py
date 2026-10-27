import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sync_keyless as keyless  # noqa: E402

# 2026-10-28 03:20（台北）由 GitHub 實抓（gate-probe url-probe 40567675702）：
# 證交所日報 rwd MI_INDEX?date=20261027&type=IND 已有 10-27；OpenAPI MI_INDEX 仍停在 10-22。
F = Path(__file__).resolve().parent / "fixtures"
DAILY = (F / "twse_mi_index_ind_20261027.json").read_bytes()
OPENAPI = (F / "twse_openapi_mi_index_20261028.json").read_bytes()


class R(io.BytesIO):
    headers = {"Content-Type": "application/json; charset=utf-8"}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def fake(url_or_request, *a, **k):
    url = getattr(url_or_request, "full_url", url_or_request)
    if "rwd/zh/afterTrading/MI_INDEX" in url:
        return R(DAILY) if "date=20261027" in url else R(json.dumps({"stat": "很抱歉，沒有符合條件的資料!"}).encode())
    if "openapi.twse.com.tw" in url:
        return R(OPENAPI)
    raise AssertionError(url)


class TwseSector(unittest.TestCase):
    def test_daily_report_supplies_same_day_sector_closes(self):
        with patch.object(keyless, "urlopen", fake):
            got = {m: keyless.twse_sector_metric(m, "2026-10-27") for m in keyless.TWSE_SECTOR_LABELS}
        self.assertEqual(got["TWSE_ELECTRONIC"]["value"], 2867.31)
        self.assertEqual(got["TWSE_SEMICONDUCTOR"]["value"], 1529.82)
        self.assertEqual(got["TWSE_FINANCIAL"]["value"], 3770.57)
        self.assertEqual(got["TWSE_SHIPPING"]["value"], 217.51)
        self.assertEqual(got["TWSE_STEEL"]["value"], 126.74)
        self.assertTrue(all(v["date"] == "2026-10-27" and "date=20261027&type=IND" in v["source"] for v in got.values()))

    def test_lagging_openapi_is_not_accepted_for_a_newer_session(self):
        # 日報沒有該日（例如尚未公布）→ 退到 OpenAPI；OpenAPI 仍是 10-22 → 兩者都不同日 → 不收（沿用舊值並標過期，不補值）
        with patch.object(keyless, "urlopen", fake):
            with self.assertRaises(ValueError) as ctx:
                keyless.twse_sector_metric("TWSE_ELECTRONIC", "2026-10-28")
        self.assertIn("2026-10-22", str(ctx.exception))

    def test_openapi_backup_still_works_when_it_is_current(self):
        # 日報逾時 → OpenAPI 備援；OpenAPI 與加權指數同日（10-22）就收
        def only_openapi(url_or_request, *a, **k):
            url = getattr(url_or_request, "full_url", url_or_request)
            if "rwd/zh/afterTrading/MI_INDEX" in url:
                raise TimeoutError("daily report timed out")
            return R(OPENAPI)
        with patch.object(keyless, "urlopen", only_openapi):
            got = keyless.twse_sector_metric("TWSE_ELECTRONIC", "2026-10-22")
        self.assertEqual(got["date"], "2026-10-22")
        self.assertIn("openapi.twse.com.tw", got["source"])


if __name__ == "__main__":
    unittest.main()
