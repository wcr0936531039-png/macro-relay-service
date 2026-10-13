import datetime as dt
import unittest
import math
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
    def test_non_finite_prices(self):
        for price in (float('nan'),float('inf'),float('-inf'),True):
            with self.subTest(price=repr(price)):
                data=self.make_data()
                data['histories']['SPY'][0]['close']=price
                result=validate(data,dt.datetime(2026,10,14,tzinfo=dt.timezone.utc))
                self.assertIn('SPY:BAD_PRICE',result['issues'])
    def test_invalid_row_date(self):
        data=self.make_data()
        data['histories']['SPY'][0]['date']='2026-09-31'
        result=validate(data,dt.datetime(2026,10,14,tzinfo=dt.timezone.utc))
        self.assertIn('SPY:INVALID_ROW_DATE',result['issues'])
    def test_malformed_input_fails_closed(self):
        now=dt.datetime(2026,10,14,tzinfo=dt.timezone.utc)
        self.assertEqual(validate([],now)['status'],'UNKNOWN')
        self.assertIn('INVALID_ROOT',validate(None,now)['issues'])
        for bad in ([], 'bad', 7):
            data=self.make_data()
            data['histories']=bad
            self.assertIn('INVALID_CONTAINERS',validate(data,now)['issues'])
        data=self.make_data()
        data['histories']['SPY'][-1]=None
        result=validate(data,now)
        self.assertEqual(result['status'],'UNKNOWN')
        self.assertIn('SPY:BAD_PRICE',result['issues'])
        data=self.make_data()
        data['status']['SPY']='corrupt'
        self.assertIn('SPY:MISSING_HISTORY',validate(data,now)['issues'])
        data=self.make_data()
        data['histories']['SPY']='corrupt'
        self.assertIn('SPY:MISSING_HISTORY',validate(data,now)['issues'])
if __name__=='__main__':unittest.main()
