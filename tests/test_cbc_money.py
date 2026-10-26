import io
import sys
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sync_keyless as keyless

# 中央銀行「貨幣總計數」頁，2026-10-26 由 GitHub 取得的原始 HTML（115 年 08 月）。
PAGE = (Path(__file__).resolve().parent / "fixtures" / "cbc_AppT1_2026-10-26.html").read_text(encoding="utf-8")


def ods(rows):
    """依官方 ms.ods 的結構（table-row／table-cell、office:value、number-columns-repeated）做一個小檔。"""
    cell = lambda v: (f'<table:table-cell office:value-type="float" office:value="{v}"><text:p>{v}</text:p></table:table-cell>'
                      if isinstance(v, (int, float)) else f'<table:table-cell office:value-type="string"><text:p>{v}</text:p></table:table-cell>')
    head = ('<table:table-row>' + cell('民國') + cell('M1A(日平均)') + '<table:table-cell table:number-columns-repeated="1"/>' + cell('M1A(期底)')
            + '<table:table-cell/>' + cell('M1B(日平均)') + '<table:table-cell/>' + cell('M1B(期底)') + '<table:table-cell/>'
            + cell('M2(日平均)3,4,6') + '<table:table-cell/>' + cell('M2(期底)3,4,6') + '<table:table-cell/></table:table-row>')
    body = ''.join('<table:table-row>' + ''.join(cell(v) for v in r) + '<table:table-cell table:number-columns-repeated="16367"/></table:table-row>' for r in rows)
    xml = ('<?xml version="1.0" encoding="UTF-8"?><office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
           'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
           f'<office:body><office:spreadsheet><table:table>{head}{body}</table:table></office:spreadsheet></office:body></office:document-content>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        z.writestr("content.xml", xml)
    return buf.getvalue()


# 數字照官方 ms.ods 115 年 07、08 月列。
ROWS = [["115年07月", 127163, 8.28, 129356, 9.69, 305309, 7.34, 304517, 6.11, 702248, 7.42, 701532, 6.58],
        ["115年08月", 128271, 8.86, 128155, 8.34, 307508, 6.65, 309594, 7.18, 706780, 6.79, 709110, 6.92]]


class CbcMoneySupplyTests(unittest.TestCase):
    def test_page_gives_month_daily_average_yoy_and_ods_link(self):
        got = keyless.cbc_money_page(PAGE)
        self.assertEqual(got["date"], "2026-08-01")
        self.assertEqual((got["m1b_yoy"], got["m2_yoy"]), (6.65, 6.79))
        self.assertRegex(got["ods_url"], r"^https://www\.cbc\.gov\.tw/tw/dl-\d+-[0-9a-f]+\.html$")

    def test_ods_history_uses_daily_average_columns(self):
        rows = keyless.cbc_money_history(ods(ROWS))
        self.assertEqual([r["date"] for r in rows], ["2026-07-01", "2026-08-01"])
        self.assertEqual(rows[-1], {"date": "2026-08-01", "value": -0.14, "m1b_yoy": 6.65, "m2_yoy": 6.79})
        self.assertEqual(rows[0]["value"], round(7.34 - 7.42, 4))

    def test_metric_cross_checks_page_and_ods(self):
        class Resp:
            def __init__(self, body): self.body = body
            def read(self, n=-1): return self.body
            def __enter__(self): return self
            def __exit__(self, *a): return False
        def fake(req, timeout=0):
            return Resp(PAGE.encode("utf-8") if "AppT1" in req.full_url else ods(ROWS))
        with patch.object(keyless, "urlopen", fake):
            item = keyless.cbc_money_supply_metric()
        self.assertEqual(item["history"][-1], {"date": "2026-08-01", "value": -0.14})
        self.assertEqual(len(item["history"]), 2)
        self.assertIn("一致", item["method"])
        mismatch = [r[:] for r in ROWS]; mismatch[-1][6] = 9.99
        def fake2(req, timeout=0):
            return Resp(PAGE.encode("utf-8") if "AppT1" in req.full_url else ods(mismatch))
        with patch.object(keyless, "urlopen", fake2):
            item = keyless.cbc_money_supply_metric()
        self.assertEqual(item["history"], [{"date": "2026-08-01", "value": -0.14}], "a mismatching file is not used; the page value stands alone")
        self.assertIn("核對未完成", item["method"])

    def test_changed_page_is_refused(self):
        with self.assertRaises(ValueError):
            keyless.cbc_money_page("<html>維護中</html>")


if __name__ == "__main__":
    unittest.main()
