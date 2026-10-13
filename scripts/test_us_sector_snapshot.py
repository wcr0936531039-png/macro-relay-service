import datetime as dt
import unittest
from check_us_sector_snapshot import validate,TICKERS
class SnapshotTests(unittest.TestCase):
    def make_data(self, end=dt.date(2026,10,13)):
        rows=[{'date':(end-dt.timedelta(days=20-i)).isoformat(),'close':100+i} for i in range(21)]
        return {'schema_version':1,'histories':{t:list(rows) for t in TICKERS},'status':{t:{'status':'ok','observed_at':end.isoformat()} for t in TICKERS}}
    def test_missing(self):
        result=validate({},dt.datetime(2026,10,14,tzinfo=dt.timezone.utc))
        self.assertEqual(result['status'],'UNKNOWN')
        self.assertIn('SYMBOL_COVERAGE',result['issues'])
    def test_complete(self):
        result=validate(self.make_data(),dt.datetime(2026,10,14,tzinfo=dt.timezone.utc))
        self.assertEqual(result['status'],'OK')
    def test_stale(self):
        result=validate(self.make_data(dt.date(2026,9,20)),dt.datetime(2026,10,14,tzinfo=dt.timezone.utc))
        self.assertIn('STALE_OR_FUTURE_DATA',result['issues'])
    def test_invalid_row_date(self):
        data=self.make_data()
        data['histories']['SPY'][0]['date']='2026-09-31'
        result=validate(data,dt.datetime(2026,10,14,tzinfo=dt.timezone.utc))
        self.assertIn('SPY:INVALID_ROW_DATE',result['issues'])
if __name__=='__main__':unittest.main()
