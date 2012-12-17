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
    for entry in feed.entry:
        try:
            html += "<li>".decode('utf8') + unicode(print_entry.getHtmlEntry(entry)) + "</li>".decode('utf8')
        except:
            pass
    html += u"</ol></body></html>"
    
    return html               
    