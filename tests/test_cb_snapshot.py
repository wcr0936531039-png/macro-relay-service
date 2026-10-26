import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sync_cb  # noqa: E402

# 2026-10-26 由 GitHub 取得的官方原始回應（gate-probe url-probe 40329651034、40329998169）：
# 櫃買 bond_ISSBD5（只留 2 列）、bond_ISSBD6（全部 29 列）、cbnote 索引、觀測站 CBTRN202609.htm（Big5 原檔）。
F = Path(__file__).resolve().parent / "fixtures"
DOM = (F / "tpex_bond_ISSBD5_2026-10-26.json").read_bytes()
OVS = (F / "tpex_bond_ISSBD6_2026-10-26.json").read_bytes()
IDX = (F / "tpex_cbnote_2026-10-26.json").read_bytes()
CBTRN = (F / "mops_CBTRN202609.htm").read_bytes()


def fake(url, accept):
    return {sync_cb.REGISTRIES["domestic"]: DOM, sync_cb.REGISTRIES["overseas"]: OVS, sync_cb.INDEX_URL: IDX,
            "https://mopsov.twse.com.tw/nas/t120/CBTRN202609.htm": CBTRN}[url]


class CbSnapshot(unittest.TestCase):
    def test_real_files(self):
        out = sync_cb.build(fetcher=fake)
        self.assertEqual(out["errors"], [])
        dom = out["registries"]["domestic"]
        self.assertEqual(dom["source_url"], "https://www.tpex.org.tw/openapi/v1/bond_ISSBD5_data")
        self.assertEqual(len(dom["sha256"]), 64)
        phison = [r for r in dom["rows"] if r["IssuerCode"] == "8299"]
        self.assertEqual(len(phison), 1)
        self.assertEqual(set(phison[0]), set(sync_cb.KEEP))
        self.assertEqual(sum(r["IssuerCode"] == "8299" for r in out["registries"]["overseas"]["rows"]), 2)
        m = out["monthly"]
        self.assertEqual(m["month"], "2026-09")
        self.assertEqual(m["source_url"], "https://mopsov.twse.com.tw/nas/t120/CBTRN202609.htm")
        # 群聯三：觀測站 9 月報轉換價 2,468.80，115/07/06 重設（與網站 v236 測試同一筆）
        self.assertEqual(m["prices"]["82993"], {"issuer": "8299", "price": 2468.8, "resetDate": "2026-07-06"})
        self.assertGreater(len(m["prices"]), 300)

    def test_failed_part_keeps_previous_copy_with_its_old_time(self):
        prev = sync_cb.build(fetcher=fake)
        prev["registries"]["domestic"]["fetched_at"] = "2026-10-25T01:00:00+00:00"

        def broken(url, accept):
            if url == sync_cb.REGISTRIES["domestic"]:
                raise TimeoutError("read timed out")
            return fake(url, accept)
        out = sync_cb.build(prev, fetcher=broken)
        self.assertEqual(out["registries"]["domestic"]["fetched_at"], "2026-10-25T01:00:00+00:00")
        self.assertEqual(out["errors"][0]["part"], "domestic")

    def test_month_mismatch_and_bad_index_are_rejected(self):
        with self.assertRaises(ValueError):
            sync_cb.parse_monthly(CBTRN, "2026-08")
        with self.assertRaises(ValueError):
            sync_cb.latest_monthly(b'{"stat":"ok","tables":[{"data":[["115/09","https://evil.example/CBTRN202609.htm"]]}]}')


if __name__ == "__main__":
    unittest.main()
