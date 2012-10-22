import print_entry
import gdata.youtube.service

def PrintVideoFeed(feed):
    
    # A list of urls.
    pages = []
    for entry in feed.entry:
        pages.append(print_entry.PrintEntryDetails(entry))
    
    return pages
        
# Print the standard video feed.        
def GetAndPrintStandardFeeds():
    yt_service = gdata.youtube.service.YouTubeService()
    
    # Print a custom feed by passing uri.
    pages = PrintVideoFeed(yt_service.GetYouTubeVideoFeed('http://gdata.youtube.com/feeds/api/standardfeeds/JP/most_viewed'))
    # List the urls in the feed.
    
    print "\n*************************************************"
    print "The list of video pages:"
    for url in pages:
        print url
    
    # Print some standard video feeds.
#    PrintVideoFeed(yt_service.GetTopRatedVideoFeed())
#    PrintVideoFeed(yt_service.GetMostViewedVideoFeed())
#    PrintVideoFeed(yt_service.GetRecentlyFeaturedVideoFeed())
#    PrintVideoFeed(yt_service.GetWatchOnMobileVideoFeed())
#    PrintVideoFeed(yt_service.GetTopFavoritesVideoFeed())
#    PrintVideoFeed(yt_service.GetMostRecentVideoFeed())
#    PrintVideoFeed(yt_service.GetMostDiscussedVideoFeed())
#    PrintVideoFeed(yt_service.GetMostLinkedVideoFeed())
#    PrintVideoFeed(yt_service.GetMostRespondedVideoFeed())
#    

# Test the result.
if __name__ == '__main__':
    GetAndPrintStandardFeeds()
    
            