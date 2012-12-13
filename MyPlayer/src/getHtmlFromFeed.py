import print_entry
# Given a feed, return a html string that represent the feed.
def getHtmlFeedDescription(feed):
    html = u'''
    <html xmlns="http://www.w3.org/1999/xhtml" lang="vi" xml:lang="vi" dir="ltr">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
          <title>Search result</title>
    </head>
    <body>
    '''
    #html = '<html><head><meta http-equiv="Content-Type" content="text/html"; "charset=utf-8"><title>Search Result</title></head><body><ol>'
    try:
        for entry in feed.entry:
            html += u"<li>%s</li>" % print_entry.getHtmlEntry(entry)
    except:
        html += u'<font color="red">Getting search result: Error'
    html += u"</ol></body></html>"
    
    return html               
    