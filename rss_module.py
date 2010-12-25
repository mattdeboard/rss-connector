import sys
import feedparser
from calendar import timegm
from time import gmtime

#To-Do:
# 1. More authoritative manner of determining authenticity of RSS url
# 2. Regex matching for more reliable determination of what key,value pair from the feed to use as the timestamp
#    field
#

def rssdownload(feedurl, last_reference):
	messages = []
	feed = feedparser.parse(feedurl)
	try:
	    feed.feed.title
	except AttributeError:
	    return 'The URL provided does not appear to be a valid RSS feed.'
	for item in feed.entries:
	    if timegm(item.updated_parsed) > last_reference:
                messages.append({'url':item.link,
                                 'timestamp':item.updated_parsed,
                                 'description':item.title,
                                 'extra':feed.feed.link,
                                 'refer':''})
	last_ref = timegm(messages[len(messages)-1]['timestamp'])
	return{'messages':messages,
               'last_reference':last_ref,
               'protected':False}
	
if __name__ == "__main__":
    sample_timestamp = timegm(gmtime()) + 15000 #41 minutes prior to start of the test, simply for testing purposes
    g = rssdownload(sys.argv[1], sample_timestamp)
    try:
    	assert type(g) == dict
    except AssertionError:
    	print g
    else:
    	print g['messages'][0]
    	print 'The sampled feed is %d items long. The above entry is the first item in the list.' % len(g['messages'])
    finally:
    	print 'Unhandled exceptions, if any, below:'
