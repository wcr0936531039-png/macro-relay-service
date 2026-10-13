import unittest
from us_sector_feed import build,TICKERS
class FeedTests(unittest.TestCase):
    def test_complete(self):
        rows=[{'date':'2026-09-'+str(i).zfill(2),'close':100+i} for i in range(1,22)]
        data=build(lambda _:rows)
        self.assertEqual(set(data['histories']),set(TICKERS))
        self.assertTrue(all(x['status']=='ok' for x in data['status'].values()))
    def test_error_isolation(self):
        def failing(_): raise TimeoutError()
        data=build(failing)
        self.assertTrue(all(x['status']=='UNKNOWN' for x in data['status'].values()))
        self.assertTrue(all(x==[] for x in data['histories'].values()))
if __name__=='__main__':unittest.main()
