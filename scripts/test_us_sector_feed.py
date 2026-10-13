import unittest
import io
import json
from unittest.mock import patch
from us_sector_feed import build,fetch,TICKERS
class FeedTests(unittest.TestCase):
    def test_complete(self):
        rows=[{'date':'2026-09-'+str(i).zfill(2),'close':100+i} for i in range(1,22)]
        data=build(lambda _:rows)
        self.assertEqual(set(data['histories']),set(TICKERS))
        self.assertTrue(all(x['status']=='ok' for x in data['status'].values()))
    def test_chart_rejects_truncated_and_duplicate_dates(self):
        def load(chart):
            body={'chart':{'result':[chart]}}
            with patch('us_sector_feed.urllib.request.urlopen',return_value=io.BytesIO(json.dumps(body).encode())):
                return fetch('SPY')
        base={'meta':{'gmtoffset':0},'indicators':{'quote':[{'close':[100.0,101.0]}]},'timestamp':[1790000000,1790086400]}
        self.assertEqual(len(load(base)),2)
        mismatched={**base,'timestamp':[1790000000]}
        with self.assertRaisesRegex(ValueError,'CHART_LENGTH_MISMATCH'):
            load(mismatched)
        duplicated={**base,'timestamp':[1790000000,1790000000]}
        with self.assertRaisesRegex(ValueError,'DUPLICATE_TRADING_DATE'):
            load(duplicated)
    def test_error_isolation(self):
        def failing(_): raise TimeoutError()
        data=build(failing)
        self.assertTrue(all(x['status']=='UNKNOWN' for x in data['status'].values()))
        self.assertTrue(all(x==[] for x in data['histories'].values()))
if __name__=='__main__':unittest.main()
