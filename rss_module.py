import sys, logging
import feedparser, lxml
from calendar import timegm
from time import gmtime


#To-Do:
# 1. More authoritative/less hacky method for determining authenticity of RSS url
# 2. Regex matching for more reliable determination of what key,value pair from the feed to use as the timestamp
#    field
# 3. Add link-mining capability.

def rssdownload(username, feedurl, last_reference=0, mode=0):
    #Added some test cases of known failing cases. You may want to add more.
    '''
    >>> rssdownload('http://www.cnn.com', timegm(gmtime())-15000)
    'The URL provided does not appear to be a valid RSS feed.'
    >>> rssdownload('http://www.cnn.com', timegm(gmtime())+15000)
    'The URL provided does not appear to be a valid RSS feed.'
    >>> rssdownload('http://feeds.feedburner.com/chrisbrogandotcom', timegm(gmtime())-15000)
    
    >>> rssdownload('http://feeds.feedburner.com/chrisbrogandotcom', timegm(gmtime())+15000)
    'There do not seem to be any new links since the last update.'
    >>> rssdownload('http://rss.cnn.com/rss/cnn_topstories', timegm(gmtime())-15000)
    
    >>> rssdownload('http://rss.cnn.com/rss/cnn_topstories', timegm(gmtime())+15000)
    'There do not seem to be any new links since the last update.'
    '''

    messages = []
    feed = feedparser.parse(feedurl)
    
    logger = logging.getLogger('proxy.rss')
    logger.debug("User %s's update URL is %s" % (username, feedurl))
    
    
    if not feed.feed.has_key['title']:
        logger.warning('User %s supplied a URL that does not seem to be a valid RSS feed (%s)' % (username, feedurl))
        return 'The URL provided does not appear to be a valid RSS feed.' #String for rendering in browser
    else:
        for item in feed.entries:
            if timegm(item.updated_parsed) > last_reference:
                messages.append({'url':item.link,
                                 'timestamp':item.updated_parsed,
                                 'description':item.title,
                                 'extra':feed.feed.link,
                                 'refer':''})
                
    if mode == 1:
        mlinks = [i['url'] for i in messages]
        deeplinks = linkminer(mlinks)
        
    if len(messages) == 0:
        logger.warning("%s doesn't have anything new for us." % feed.feed.title) 
        return 'There do not seem to be any new links since the last update.' #String for rendering in browser
    
    last_ref = timegm(messages[len(messages)-1]['timestamp'])
    
    return{'messages':messages,
           'last_reference':last_ref,
           'protected':False}

##def linkminer(mlinks):
##    for item in mlinks:
        
	
if __name__ == "__main__":
    
    def testgo(g):
        if isinstance(g, dict):
            return 'The sampled feed is %d items long.' % len(g['messages'])
        else:
            return g
        
    test_params = ['-doc', '-cust', None]
    if sys.argv[1] in test_params:
        if sys.argv[1] == '-doc':
            import doctest
            doctest.testmod()
        if sys.argv[1] == '-cust' or '':
            url = raw_input('Paste URL to test: ')
            while True:
                try:
                    timeframe = raw_input('Set last_ref to past or future [P/f]? ')
                    assert timeframe.lower() in ('', 'p', 'f')
                    break
                except AssertionError:
                    pass
            if timeframe.lower() in ('', 'p'):
                with rssdownload(url, timegm(gmtime())-15000) as test1:
                    print test1
            else:
                with rssdownload(url, timegm(gmtime())+15000) as test1:
                    print test1
            result = testgo(test1)
            print result
    else:
        print 'Valid arguments are -doc (for doctest.testmod() testing) and -cust (for custom URL/last_ref input).'
        

