import sys, logging, httplib2
import feedparser
from calendar import timegm
from time import gmtime
from lxml import etree

#To-Do:
# 1. More authoritative/less hacky method for determining authenticity of RSS url
# 2. Regex matching for more reliable determination of what key,value pair from the feed to use as the timestamp
#    field
# 3. Add link-mining capability.
# 4. Improve doctesting by adding better test cases.
# 5. Improve command-line testing.
# 6. Implement "mode 1" (deep link-mining) capabilities

def rssdownload(username, feedurl, last_reference=0):

    messages = []
    feed = feedparser.parse(feedurl)
    
    logger = logging.getLogger('proxy.rss')
    logger.debug("User %s's update URL is %s" % (username, feedurl))
    
    
    if not feed.feed.has_key['title']:
        logger.error('User %s supplied a URL that does not seem to be a valid RSS feed (%s)' % (username, feedurl))
        return {'messages':[],'last_reference':last_ref}
    else:
        for item in feed.entries:
            if timegm(item.updated_parsed) > last_reference:
                messages.append({'url':item.link,
                                 'timestamp':item.updated_parsed,
                                 'description':item.title,
                                 'extra':feed.feed.link,
                                 'refer':''})
##                
##    if mode == 1:
##        mlinks = [i['url'] for i in messages]
##        deeplinks = linkminer(mlinks)
        
    if len(messages) == 0:
        logger.warning("%s doesn't have anything new for us." % feed.feed.title) 
        return 'There do not seem to be any new links since the last update.' #String for rendering in browser
    
    last_ref = timegm(messages[len(messages)-1]['timestamp'])
    
    return{'messages':messages,
           'last_reference':last_ref,
           'protected':False}

##def linkminer(mlinks):
##    http = httplib2.Http()
##    response, content = http.request(item, 'GET')
##    html = etree.HTML(content)
##    result = etree.tostring(html, pretty_print=True, method="html")
##    
##    for item in mlinks:        
	
if __name__ == "__main__":
    
    
