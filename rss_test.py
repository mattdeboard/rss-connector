from rss_module import rssdownload as rss_module
import unittest
from calendar import timegm
from time import gmtime

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.feedurl_invalid = 'http://www.cnn.com'
        self.feedurl_valid = 'http://rss.cnn.com/rss/cnn_topstories'
        self.past = timegm(gmtime()) - 15000
        self.future = timegm(gmtime()) + 15000

    def test_bad_url_past(self):
        # Make sure an empty dict gets returned for an invalid URL
        test_feed = rss_module(self.username, self.feedurl_invalid, self.past)
        self.assertTrue(len(test_feed['messages'])==0)

    def test_bad_url_future(self):
        # Make sure an empty dict gets returned for an invalid URL
        test_feed = rss_module(self.username, self.feedurl_invalid, self.future)
        self.assertTrue(len(test_feed['messages'])==0)

    def test_good_url_past(self):
        # Make sure an empty dict gets returned for a valid URL
        test_feed = rss_module(self.username, self.feedurl_valid, self.past)
        self.assertTrue(len(test_feed['messages'])>0, 'Probably no new links found...')

    def test_good_url_future(self):
        # Make sure an empty dict gets returned for a valid URL
        test_feed = rss_module(self.username, self.feedurl_valid, self.future)
        self.assertTrue(len(test_feed['messages'])==0)

if __name__ == '__main__':
    unittest.main()
        
        
