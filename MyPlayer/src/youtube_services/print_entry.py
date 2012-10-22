# Author Le Van Huynh
# Last edited: 11-09/2012
#
# A script based on the function provided by youtube python API documentation.
# Some line removed to make it work.

import get_specific_entry

def PrintEntryDetails(entry):
    # Get the url of the entry.
    url = None
    
    
    try:
        print "\n*****************************************************************"
        print 'Video title: %s' % entry.media.title.text
        print 'Video published on: %s ' % entry.published.text
        print 'Video tags: %s' % entry.media.keywords.text      
        print 'Video watch page: %s' % entry.media.player.url
        url = entry.media.player.url
        print 'Video flash player URL: %s' % entry.GetSwfUrl()
        print 'Video duration: %s' % entry.media.duration.seconds
        # non entry.media attributes
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
        
        
        
        
    except:
        print "Exception occured!"
        
    # Return the url
    return url
        
if __name__ == '__main__':
    entry = get_specific_entry.GetEntry(video_id='the0KZLEacs')
    
    # Print the entry information.
    PrintEntryDetails(entry)
    
    
            
