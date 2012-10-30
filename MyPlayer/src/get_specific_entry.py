# Get a specific entry.

import gdata.youtube.service

# Return the entry if no error occurs, return 'None' otherwise.
def GetEntry(video_id):
    # Initialize the service.
    yt_service = gdata.youtube.service.YouTubeService()
    
    # Get the entry.
    try:
        entry = yt_service.GetYouTubeVideoEntry(video_id = video_id)
    except:
        entry = None        
    
    # Return the entry.
    return entry
    