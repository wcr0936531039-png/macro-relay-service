import unittest
from us_sector_publish_guard import should_publish

def snapshot(day):
    return {'status':{'SPY':{'status':'ok','observed_at':day}}}

class PublishGuardTests(unittest.TestCase):
    def test_newer_candidate(self):
        self.assertTrue(should_publish(snapshot('2026-10-14'),snapshot('2026-10-13')))
    def test_equal_date_is_allowed(self):
        self.assertTrue(should_publish(snapshot('2026-10-13'),snapshot('2026-10-13')))
    def test_older_candidate_is_blocked(self):
        self.assertFalse(should_publish(snapshot('2026-10-12'),snapshot('2026-10-13')))
    def test_empty_remote(self):
        self.assertTrue(should_publish(snapshot('2026-10-13'),{}))
    def test_invalid_candidate_rejected(self):
        with self.assertRaisesRegex(ValueError,'INVALID_CANDIDATE_DATE'):
            should_publish({'status':{}},snapshot('2026-10-13'))

if __name__=='__main__':
    unittest.main()
