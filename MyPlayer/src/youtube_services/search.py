import gdata.youtube.service
import print_video_feed

def SearchAndPrint(search_terms):
    # Init service.
    yt_service = gdata.youtube.service.YouTubeService()
    
    # Init search query.
    query = gdata.youtube.service.YouTubeVideoQuery()    
    query.vq = search_terms
    query.orderby = 'viewCount'
    query.racy = 'include'
    
    # Run the query.
    feed = yt_service.YouTubeQuery(query)
    
    # Print the result.
    print_video_feed.PrintVideoFeed(feed)

if __name__ == '__main__':
    search_term = unicode(raw_input("Enter the search term: "))
    SearchAndPrint(search_term)
        
    
    
    