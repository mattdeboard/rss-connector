import sys, logging, unittest
import feedparser
from calendar import timegm
from time import gmtime
from operator import itemgetter
from lxml import html

##Copyright (c) 2010, 2011 Matt DeBoard - mattdeboard.net - matt.deboard@gmail.com
##
##Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files
##(the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge,
##publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do
##so, subject to the following conditions:
##
##The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
##
##THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
##MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
##FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
##WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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

def rssdownload(username, feedurl, last_reference=0, mode=0):
    ''' --> rssdownload(username, feedurl, last_reference=0)

        'username' is used exclusively for logging purposes at this time.
        'feedurl' must be a valid RSS feed. Validation is performed by checking
        the parsed data from the URL for the <title> tag, which is RSS 2.0 standard.
        If feedurl is not a valid RSS URL by that standard, an empty dictionary object
        is returned, and an error is logged.

        'last_reference' is the Unix time (UTC Epoch) of the last time this URL was polled.
        This time is determined by getting the time the most recent article was last updated.
        Only links added or updated after last_reference are returned to the user. If there
        are no new links, an error is logged and an empty dictionary object is returned.

        mode 0 = default. mode 1 = will search the feed entries for some fields commonly used
        to contain body text. If these fields are found, they will be parsed for links, and be
        returned from this function as a separate dictionary object.'''

    deeplinks = {}
    messages = []
    feed = feedparser.parse(feedurl)

    try:
        a,b = bozocheck(feed)
    except TypeError:
        pass

    #Any of the items in srch can contain body text to parse for links
    srch = ['content', 'summary', 'subtitle'] 
    
    logger = logging.getLogger('proxy.rss')
    logger.debug("User %s's update URL is %s" % (username, feedurl))
    
    try:
        assert feed.feed.has_key('title')
    except AssertionError:
        logger.error('User %s supplied a URL that does not seem to be a valid RSS feed (%s)' % (username, feedurl))
        return {'messages':[],'last_reference':last_reference, 'protected':False}

    for item in feed.entries:
        if timegm(item.updated_parsed) > last_reference:
            messages.append({'url':item.link,
                             'timestamp':timegm(item.updated_parsed),
                             'description':item.title,
                             'extra':feed.feed.title,
                             'refer':''})
        if mode == 1:
            for k in srch:
                if item.has_key(k) and type(item[k]) == (unicode or str):
                    deeplinks[item.link] = {'mined_links_%s' % k:linkmine(item[k])}
        
    if len(messages) == 0:
        if not a:
            logger.error("%s doesn't have anything new for us." % feed.feed.title) 
        else:
            logger.warning("Malformed data at %s may have  prevented proper update. Exception %s" %
                           (feed.feed.title, a) +
                           "on line %d" % b) 
        return {'messages':[], 'last_reference':last_reference, 'protected':False}
                           
    messages.sort(key=itemgetter('timestamp'))
    last_ref = messages[len(messages)-1]['timestamp']
    
    feed_data = {'messages':messages,
                 'last_reference':last_ref,
                 'protected':False}

    if len(deeplinks):
        return feed_data, deeplinks
    else: return feed_data

def linkmine(summary):
    return [item[2] for item in html.iterlinks(summary)]

def bozocheck(feed):
    if feed.bozo:
        return feed.bozo_exception.getMessage(),feed.bozo_exception.getLineNumber()
    else:
        return
