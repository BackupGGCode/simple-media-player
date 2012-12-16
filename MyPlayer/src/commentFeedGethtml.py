import get_specific_entry
import gdata.youtube
def getHtmlForCommentFeed(comment):
    '''
    Given a comment object, return a representing html string.
    '''
    xml_string =  comment.ToString()
    print xml_string
    

if __name__ == '__main__':
    yt_service = gdata.youtube.service.YouTubeService()
    #entry = get_specific_entry(video_id='the0KZLEacs')
    comment_feed = yt_service.GetYouTubeVideoCommentFeed(video_id='the0KZLEacs')
    getHtmlForCommentFeed(comment_feed.entry[0])