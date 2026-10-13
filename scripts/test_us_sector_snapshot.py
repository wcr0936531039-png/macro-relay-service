import datetime as dt
import unittest
from check_us_sector_snapshot import validate,TICKERS
class SnapshotTests(unittest.TestCase):
    def test_missing(self):
        result=validate({},dt.datetime(2026,10,14,tzinfo=dt.timezone.utc))
        self.assertEqual(result['status'],'UNKNOWN')
        self.assertIn('SYMBOL_COVERAGE',result['issues'])
    def test_complete(self):
        rows=[{'date':(dt.date(2026,10,13)-dt.timedelta(days=20-i)).isoformat(),'close':100+i} for i in range(21)]
        data={'schema_version':1,'histories':{t:rows for t in TICKERS},'status':{t:{'status':'ok','observed_at':'2026-10-13'} for t in TICKERS}}
        result=validate(data,dt.datetime(2026,10,14,tzinfo=dt.timezone.utc))
        self.assertEqual(result['status'],'OK')
    def test_stale(self):
        rows=[{'date':(dt.date(2026,9,20)-dt.timedelta(days=20-i)).isoformat(),'close':100+i} for i in range(21)]
        data={'schema_version':1,'histories':{t:rows for t in TICKERS},'status':{t:{'status':'ok','observed_at':'2026-09-20'} for t in TICKERS}}
        result=validate(data,dt.datetime(2026,10,14,tzinfo=dt.timezone.utc))
        self.assertIn('STALE_OR_FUTURE_DATA',result['issues'])
if __name__=='__main__':unittest.main()
