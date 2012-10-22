import gdata.youtube.service

# Constant.
DEVELOPER_KEY = 'AI39si4rv6LckFbM0mtepQ2ptX91ij0ZLnBL3whBTkGpuc0rDQe4Z0HD9ZJRtvFCPe2J-qZTb818hp7h6N9SXEyP0oY3QwCPXQ'
# Now a client id is not needed.

def auth(email, password):
    # Setup service.
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.email = email
    yt_service.password = password
    yt_service.source = 'youtube_interface'
    yt_service.developer_key = DEVELOPER_KEY
    
    # Login.
    yt_service.ProgrammaticLogin()
    
    return yt_service

def GetAndPrintVideoFeed(uri):
    yt_service = gdata.youtube.service.YouTubeService()
    feed = yt_service.GetYouTubeVideoFeed(uri)
    for entry in feed.entry:
        PrintEntryDetails(entry)

def PrintEntryDetails(entry):
    print 'Video title: %s' % entry.media.title.text
    print 'Video published on: %s ' % entry.published.text
    print 'Video description: %s' % entry.media.description.text
    print 'Video tags: %s' % entry.media.keywords.text
    print 'Video watch page: %s' % entry.media.player.url
    print 'Video flash player URL: %s' % entry.GetSwfUrl()
    print 'Video duration: %s' % entry.media.duration.seconds

    # non entry.media attributes
    print 'Video geo location: %s' % entry.geo.location()
    print 'Video view count: %s' % entry.statistics.view_count
    print 'Video rating: %s' % entry.rating.average

    # show alternate formats
    for alternate_format in entry.media.content:
        if 'isDefault' not in alternate_format.extension_attributes:
            print 'Alternate format: %s | url: %s ' % (alternate_format.type,
                                                 alternate_format.url)

    # show thumbnails
    for thumbnail in entry.media.thumbnail:
        print 'Thumbnail url: %s' % thumbnail.url        
