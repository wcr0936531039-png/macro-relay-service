import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sync_keyless as keyless

# EIA WCESTUS1 歷史頁，2026-10-26 由 GitHub 取得（gate-probe url-probe 40257314055）；保留最後 3 個月與發布日表格。
PAGE = (Path(__file__).resolve().parent / "fixtures" / "eia_wcestus1_leaf_2026-10-26.html").read_text(encoding="utf-8")
URL = "https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?f=W&n=PET&s=WCESTUS1"


class EiaReleaseDates(unittest.TestCase):
    def test_real_page_release_and_next_release(self):
        entry = keyless.eia_crude_from_page(PAGE, URL)
        self.assertEqual(entry["date"], "2026-10-16")
        self.assertAlmostEqual(entry["value"], 412.517)
        self.assertEqual(entry["raw_thousand_barrels"], 412517)
        self.assertEqual(entry["release_date"], "2026-10-21")
        self.assertEqual(entry["next_release_date"], "2026-10-28")
        self.assertEqual(len(entry["page_sha256"]), 64)
        self.assertTrue(all(set(p) == {"date", "value"} for p in entry["history"]))
        self.assertEqual([p["date"] for p in entry["history"][-2:]], ["2026-10-09", "2026-10-16"])

    def test_missing_or_implausible_dates_are_not_written(self):
        no_dates = PAGE.replace("Release Date: 10/21/2026", "").replace("Next Release Date: 10/28/2026", "")
        entry = keyless.eia_crude_from_page(no_dates, URL)
        self.assertNotIn("release_date", entry)
        self.assertNotIn("next_release_date", entry)
        far = PAGE.replace("Release Date: 10/21/2026", "Release Date: 11/30/2026")
        self.assertNotIn("release_date", keyless.eia_crude_from_page(far, URL))
        bad_next = PAGE.replace("Next Release Date: 10/28/2026", "Next Release Date: 12/30/2026")
        entry = keyless.eia_crude_from_page(bad_next, URL)
        self.assertEqual(entry["release_date"], "2026-10-21")
        self.assertNotIn("next_release_date", entry)


if __name__ == "__main__":
    unittest.main()
