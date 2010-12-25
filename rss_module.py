import sys, logging, unittest
import feedparser
from calendar import timegm
from time import gmtime

#To-Do:
# 
# 2. Regex matching for more reliable determination of what key,value pair from the feed to use as the timestamp
#    field
# 3. Implement "mode 1" (deep link-mining) capabilities
# 
# 
#

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.feedurl_invalid = 'http://www.cnn.com'
        self.feedurl_valid = 'http://rss.cnn.com/rss/cnn_topstories'
        self.past = timegm(gmtime()) - 15000
        self.future = timegm(gmtime()) + 15000

    def test_bad_url_past(self):
        # Make sure an empty dict gets returned for an invalid URL
        test_feed = rssdownload(self.username, self.feedurl_invalid, self.past)
        self.assertTrue(len(test_feed['messages'])==0)

    def test_bad_url_future(self):
        # Make sure an empty dict gets returned for an invalid URL
        test_feed = rssdownload(self.username, self.feedurl_invalid, self.future)
        self.assertTrue(len(test_feed['messages'])==0)

    def test_good_url_past(self):
        # Make sure an empty dict gets returned for a valid URL
        test_feed = rssdownload(self.username, self.feedurl_valid, self.past)
        self.assertTrue(len(test_feed['messages'])>0, 'Probably no new links found...')

    def test_good_url_future(self):
        # Make sure an empty dict gets returned for a valid URL
        test_feed = rssdownload(self.username, self.feedurl_valid, self.future)
        self.assertTrue(len(test_feed['messages'])==0)

def rssdownload(username, feedurl, last_reference=0):
    ''' --> rssdownload(username, feedurl, last_reference=0)

        'username' is used exclusively for logging purposes at this time.
        'feedurl' must be a valid RSS feed. Validation is performed by checking
        the parsed data from the URL for the <title> tag, which is RSS 2.0 standard.
        If feedurl is not a valid RSS URL by that standard, an empty dictionary object
        is returned, and an error is logged.

        'last_reference' is the Unix time (UTC Epoch) of the last time this URL was polled.
        Only links added or updated after last_reference are returned to the user. If there
        are no new links, an error is logged and an empty dictionary object is returned.'''

    messages = []
    feed = feedparser.parse(feedurl)
    
    logger = logging.getLogger('proxy.rss')
    logger.debug("User %s's update URL is %s" % (username, feedurl))
    
    try: feed.feed.title
    except AttributeError:
        logger.error('User %s supplied a URL that does not seem to be a valid RSS feed (%s)' % (username, feedurl))
        return {'messages':[],'last_reference':last_reference, 'protected':False}
    for item in feed.entries:
        if timegm(item.updated_parsed) > last_reference:
            messages.append({'url':item.link,
                             'timestamp':item.updated_parsed,
                             'description':item.title,
                             'extra':feed.feed.link,
                             'refer':''})
        
    if len(messages) == 0:
        logger.error("%s doesn't have anything new for us." % feed.feed.title) 
        return {'messages':[], 'last_reference':last_reference, 'protected':False}
    
    last_ref = timegm(messages[len(messages)-1]['timestamp'])
    
    return{'messages':messages,
           'last_reference':last_ref,
           'protected':False}

if __name__ == '__main__':
    unittest.main()
    
