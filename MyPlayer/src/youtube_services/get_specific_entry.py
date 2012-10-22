# Get a specific entry.

import gdata.youtube.service

def GetEntry(video_id):
    # Initialize the service.
    yt_service = gdata.youtube.service.YouTubeService()
    
    # Get the entry.
    entry = yt_service.GetYouTubeVideoEntry(video_id = video_id)
    
    # Return the entry.
    return entry
    