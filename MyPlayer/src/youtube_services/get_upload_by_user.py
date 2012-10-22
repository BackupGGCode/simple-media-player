# Author: Le Van Huynh
# Last modified; 11/09/2012
# TODO: error handling.

import gdata.youtube.service
from print_video_feed import PrintVideoFeed

def GetAndPrintUserUploads(username):
    
    # Init service
    yt_service = gdata.youtube.service.YouTubeService()
    
    # Construct the uri
    uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads' % username
    
    # Get the feed.
    PrintVideoFeed(yt_service.GetYouTubeVideoFeed(uri))
    

if __name__ == '__main__':
    GetAndPrintUserUploads('BBCComedy')
        
    
    