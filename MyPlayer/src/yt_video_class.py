# A simple video class that hold information about  a video.
# This will be useful when you want to create a play list or a list of videos
# to download.
class Video:
    def init(self, link = None, direct_link = None, name = None):
        self.setProperty(link, direct_link, name)

    def setProperty(self, link, direct_link, name):
        self.name = name # The name of the video
        self.link = link # link to the video page
        self.direct_link = direct_link # The link to the video file

    # Get the name of the video.
    def getName(self):
        return self.name

    # get the link to the Youtube page.
    def getLink(self):
        return self.link

    # get the direct link to the video file.
    def getDirectLink(self):
        return self.link
    
