#/Test some functions
# Author: Huynh
# Last modified date: 12/09/2010
# TODO: write a GUI.

from print_video_feed import PrintVideoFeed
import gdata.youtube.service
from print_entry import PrintEntryDetails
from get_specific_entry import GetEntry
from search import SearchAndPrint
from get_upload_by_user import GetAndPrintUserUploads
import commands
import urllib2
from urllib2 import Request

while True:
    # Print a menu.
    print "Choose a function"
    print "***************************************"
    print "1. View standard feeds information"
    print "2. View specific video information"
    print "3. Search for video"
    print "4. Get a specific user's uploads"
    print "5. Upload a video --NOT IMPLEMENTED--"
    print "6. Delete an uploaded video --NOT IMPLEMENTED--"
    print "Choose a function numbers or enter 0 to quit"
    
    number = int(raw_input("\nChoose a function: "))
    if number < 1 or number > 6:
        break
    # Intialize service.
    yt_service = gdata.youtube.service.YouTubeService()
    
    if number == 1:
        # View standard feed information
        # Print a list of feeds            
        PrintVideoFeed(yt_service.GetTopRatedVideoFeed())
        PrintVideoFeed(yt_service.GetMostViewedVideoFeed())
        PrintVideoFeed(yt_service.GetRecentlyFeaturedVideoFeed())
        PrintVideoFeed(yt_service.GetWatchOnMobileVideoFeed())
        PrintVideoFeed(yt_service.GetTopFavoritesVideoFeed())
        PrintVideoFeed(yt_service.GetMostRecentVideoFeed())
        PrintVideoFeed(yt_service.GetMostDiscussedVideoFeed())
        PrintVideoFeed(yt_service.GetMostLinkedVideoFeed())
        PrintVideoFeed(yt_service.GetMostRespondedVideoFeed())
    elif number == 2:
        # Get the entry.
        video_id = raw_input("Enter video ID: ")
        entry = GetEntry(video_id)
        
        url = urllib2.urlopen(entry.GetSwfUrl())
        print url.info()
        
        #Print the entry information.
        PrintEntryDetails(entry)
        
        #Play the entry
        #output = commands.getstatusoutput("'C:\Program Files\VideoLAN\VLC\vlc.exe' '%s'" % finalurl)
        #print output        
        
    elif number == 3:
        #Enter the search term.
        search_term = unicode(raw_input("Enter the search term: "))
        SearchAndPrint(search_term)       
    elif number == 4:
        username = raw_input("Enter the username: ")
        GetAndPrintUserUploads(username)
    else:
        print "Sorry, this function is not implemented."
        