# Author Le Van Huynh
# Last edited: 11-09/2012

import get_specific_entry
import re

# Print the information about an entry in html form.
def getHtmlEntry(entry):
    try:
        url = entry.GetSwfUrl()
    except:
        url = ""
    try:
        title = entry.media.title.text
    except:
        title = " "
    try:            
        thumbnail =  entry.media.thumbnail[0].url
    except:
        thumbnail = ""
    try:  
        published = entry.published.text
    except:
        published = "N/A"
    try:
        keywords = entry.media.keywords.text
    except:
        keywords = "N/A"
    try:
        duration = entry.media.duration.seconds
    except:
        duration = "0"
    try:
        viewCount = entry.statistics.view_count
    except:
        viewCount = "N/A"
    try:
        rating = entry.rating.average                        
    except:
        rating = "N/A"    
    html = '''
    <a href="%s">%s</a>
    <table>
        <tr>
            <td><img src="%s" alt="Thumbnails" width="150" height="100" /><td>
            <td>
            <table>
            <tr><td>Published</td><td>%s</td></tr>
            <tr><td>Keywords</td><td>%s</td></tr>
            <tr><td>Duration</td><td>%s</td></tr>
            <tr><td>View count</td><td>%s</td></tr>
            <tr><td>Rating</td><td>%s</td></tr>
            </table>
            </td>
        </tr>
    </table>
    ''' %(url, title, thumbnail, published, keywords, duration, viewCount, rating)
    
    return html
               
def getVideoId(entry):
    print "entry.text =", entry.id.text
    m = re.search(r'http://gdata.youtube.com/feeds/api/videos/(.+)$', entry.id.text)
    if m:
        youtube_id = m.group(1)
    else:
        m = re.search(r'http://gdata.youtube.com/feeds/videos/(.+)$', entry.id.text)
        if m:
            youtube_id = m.group(1)
        else:
            print "An error has occured!"
            youtube_id = None
    return youtube_id
            

if __name__ == '__main__':
    print "Getting entry"
    entry = get_specific_entry.GetEntry(video_id='cCe-2eH8gBM')
    
    print "Processing"
    # Print the entry information.
    #print getHtmlEntry(entry)
    
    print "The ID of that video is:", getVideoId(entry)
    
            
