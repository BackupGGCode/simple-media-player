# -*- coding: utf-8 *-*
###############################################################################
# A simple media player.
#
#
#

import sys
import random
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtWebKit import QWebPage, QWebSettings
import gdata

# Two additional UI module.
import about

from QtThread import GenericThread
from uploadDialog import UploadDialog
import WarningDialog
from YoutubeService import YouTubeService
from getHtmlFromFeed import getHtmlFeedDescription
import getHtmlFromFeed
import traceback

# A class represent a simple media player.
class VideoPlayer(QtGui.QMainWindow):

    def __init__(self):
        # Initialize: calling the inherited __init__ function.
        super(VideoPlayer, self).__init__()
        
        # Load the defined UI.
        uic.loadUi('../share/ui/videoplayer.ui', self)
        self.initAttributes()           
        
    def initAttributes(self):
        self.showMaximized()
        # Initialize the play list.
        self.playlist = [] # A list of links to the file to play.
        self.playlistTmp = [] # A temporary play list, use to shuffle play list.
        
        # The dock widget: show or hide?
        self.dckShown = True
        self.lineEditSearch.setFocus()   
        
        # Search thread.
        self.threadPool = []
        
        # Enable the flash plugin
        QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
        
        # Search box: Enter pressed.
        self.lineEditSearch.returnPressed.connect(self.on_btnSearchVideo_clicked)
        
        # The page showing search result.
        self.videoList.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.videoList.connect(self.videoList, QtCore.SIGNAL('linkClicked(const QUrl&)'), self.linkClicked)
        
        # Load the page for Youtube.
        self.stackedWidget.setCurrentIndex(1)
        
        # home page: youtube.com
        self.homeURL = QtCore.QUrl(r'https://youtube.com')
        
        #Load the default page.
        self.videoList.load(self.homeURL)
        
        # Make two webpages share the same session.
        if not self.videoList.page().networkAccessManager() == None:
            self.playerView.page().setNetworkAccessManager(self.videoList.page().networkAccessManager())

        # A seperate frame for login.
        self.logged_in = False
        self.yt_service = None
        self.uploadDialog = UploadDialog(self)
    
    # Click a link in the list of videos.
    def linkClicked(self, url):
        if str(url.toString()).find('youtube') != -1:
            self.addMedia(url)
    
    # User's feed.
    @QtCore.pyqtSlot()
    def on_lineeditUserFeed_returnPressed(self):
        # Start searching.
        self.threadPool.append(GenericThread(self.ytUserFeedSearch, self.lineeditUserFeed.displayText()))        
        self.disconnect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.connect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.threadPool[len(self.threadPool) - 1].start()
        self.setFocus()        
    
    # Return an instance that helps us to use youtube's services.
    def getYouTubeService(self, username = '', password = ''):
        if (username != '' and password != ''): # new instance.
                self.yt_service = YouTubeService(username, password)
                return self.yt_service
        elif self.yt_service != None:
            return self.yt_service
        else:
            self.yt_service = YouTubeService()
            return self.yt_service
    
    def ytUserFeedSearch(self, username):
        print "Searching for videos by", username
        yt_service = self.getYouTubeService()
        feed = yt_service.RetrieveUserVideosbyUsername(username)
        html = getHtmlFeedDescription(feed)
        self.emit(QtCore.SIGNAL('doneSearching(QString)'), html)
                
    #Click on the 'search' button in the search tab.
    @QtCore.pyqtSlot()
    def on_btnSearchVideo_clicked(self):
        # Get the order option.
        if self.lineEditSearch.text() == '':
            return    
        if self.rdbRelevance.isChecked():
            orderby = "relevance"
        elif self.rdbPublished.isChecked():
            orderby = "published"
        elif self.rdbView.isChecked():
            orderby = "viewCount"
        else:
            orderby = "rating"
        
        # Get the safe search option.
        if self.rdbRacyExclude.isChecked():
            racy = 'exclude'
        else:
            racy = 'include'
        
        # Get the search result number.
        max_results = int(self.spbMaxResults.cleanText())
        
        # get the search term.
        vq = self.lineEditSearch.text()
        
        # searching not done: Print the defaul message.
        self.videoList.setHtml("<html><body><h1>Searching ...</h1></body></html>")
        
        # Create a thread to do the search.        
        self.threadPool.append(GenericThread(self.ytSearch, vq, orderby, racy, max_results))        
        self.disconnect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.connect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.threadPool[len(self.threadPool) - 1].start()
        self.setFocus()
    
    # Set the content of the playlist page.
    def setHtml(self, html):
        self.videoList.setHtml(html)
    
    # Do the search.
    #TODO Re-implement using YoutubeService.
    def ytSearch(self, vq, orderby, racy, max_results):
        try:
            # Init service.
            yt_service = self.getYouTubeService()
            #vq must be converted to str.
            feed = yt_service.SearchWithVideoQuery(str(vq), orderby, racy, max_results)
            print "Done *******"
        except:
            print "Error:"
            traceback.print_last()
            feed = None
        
        print 'Getting the html'
        html = getHtmlFeedDescription(feed)
        print html
        self.emit(QtCore.SIGNAL('doneSearching(QString)'), html)

    # Event: The 'About' button is clicked
    @QtCore.pyqtSlot()
    def on_btnAbout_clicked(self):
        ab = about.About(self)
        ab.show()

    # Event: The button 'Clear Play list' is pressed.
    @QtCore.pyqtSlot()
    def on_btnClearPlayList_clicked(self):
        # Clear the original and temporal play list.
        self.playlist = []
        self.playlistTmp = []
        self.updatePlayList()

    # Event: The next button is pressed.
    @QtCore.pyqtSlot()
    def on_btnNext_clicked(self):
        if self.playlist == []:
            # Nothing to do.
            return
        # Get the reference to the current selected media.
        curIndex = self.lswPlaylist.currentRow()
        if curIndex + 1 < len(self.playlist):
            # Not the last video
            index = curIndex + 1
        else:
            # This is the last video.
            if not self.repeat:
                # No repeat: just return.
                return
            else:
                index = 0

        # Select the next media in the play list, and play it.
        self.lswPlaylist.setCurrentRow(index, QtGui.QItemSelectionModel.SelectCurrent)
        self.on_lswPlaylist_doubleClicked()

    # Action: click on the 'previous' button.
    @QtCore.pyqtSlot()
    def on_btnPrevious_clicked(self):
        if self.playlist == []:
            return

        # Get a reference of the current selected media.
        curIndex = self.lswPlaylist.currentRow()

        # If the current selected media index is greater or equal to the first
        # index of the play list...
        if curIndex > 0:
            # decrease the index of the current media.
            index = curIndex - 1
        else:
            # This is the first item in the list.
            # If the repeat mode isn't selected then do nothing.
            if not self.repeat:
                return

            # otherwise, the next media to play will be the last in the list.
            index = len(self.playlist) - 1

        # Select the previous media in the play list and play it.
        self.lswPlaylist.setCurrentRow(index, QtGui.QItemSelectionModel.SelectCurrent)
        self.on_lswPlaylist_doubleClicked()

    # Action: Click on the 'Remove media' button.
    @QtCore.pyqtSlot()
    def on_btnRemoveMedia_clicked(self):
        # For each selected media...
        for media in self.lswPlaylist.selectedItems():
            try:
                # get it's index and remove it from the play list.
                del self.playlist[self.lswPlaylist.row(media)]
            except:
                pass

        self.updatePlayList()


    # Action: click on the 'Repeat' button.
    @QtCore.pyqtSlot()
    def on_btnRepeatPlayList_clicked(self):
        self.repeat = not self.repeat

    # Action: Click on the 'Show Play list' button.
    @QtCore.pyqtSlot()
    def on_btnShowPlayList_clicked(self):
        if self.dckShown:
            self.dckPlayList.hide()
        else:
            self.dckPlayList.show()
        self.dckShown = not self.dckShown
            
    # Action: Click on the 'Shuffle Play list' button.
    @QtCore.pyqtSlot()
    def on_btnShufflePlayList_clicked(self):
        if self.playlistTmp == []:
            # this mean the play list is not shuffled.
            self.playlistTmp = self.playlist[:]

            # Now shuffle it.
            item = len(self.playlist) - 1
            while item > 0:
                index = random.randint(0, item)
                tmp = self.playlist[index]
                self.playlist[index] = self.playlist[item]
                self.playlist[item] = tmp
                item -= 1
        else:
            # Return the list to the original state.
            self.playlist = self.playlistTmp[:]
            self.playlistTmp = []

        # Update the play list.
        self.updatePlayList()

    

    # Action: Double an item in the play list to play it.
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_lswPlaylist_doubleClicked(self):
        # If the play list is empty, do nothing.
        if self.playlist == []:
            return
        
        # Get the index of model_index, use it to obtain corresponding link
        link = self.playlist[self.lswPlaylist.currentRow()];
        
        #Switch to the playerPage
        #Play the selected video.
        self.stackedWidget.setCurrentIndex(0)
        self.playerView.load(link)

    # Add to the play a link
    def addMedia(self, url):
        self.playlist.append(url)

        # update the play list.
        self.updatePlayList()

        # If the play list has been loaded and there isn't a media playing,
        # play it.
        if len(self.playlist) == 1:
            self.stackedWidget.setCurrentIndex(0)
            self.playerView.load(url)
        
    # Update the play list.
    def updatePlayList(self):
        # Remove all items in QListWidget
        self.lswPlaylist.clear()

        # add the new play list.
        for item in self.playlist:
            self.lswPlaylist.addItem(item.toString())

    
    # Select the page vie: Search result of video page.
    @QtCore.pyqtSlot()
    def on_showVideoPage_clicked(self):
        self.stackedWidget.setCurrentIndex(0)
    
    # Ask to navigate to search result page.
    @QtCore.pyqtSlot()
    def on_showSearchPage_clicked(self):
        self.stackedWidget.setCurrentIndex(1)
        
    @QtCore.pyqtSlot()
    def on_btnUpload_clicked(self):
        if not self.logged_in:
            messageBox = WarningDialog.WarningDialog(warning="You have to log in first", parent=self)
            messageBox.show()
        else:
            print "Calling the function upload"
            # Get the video information.            
            self.uploadDialog.show()
            self.connect(self.uploadDialog, QtCore.SIGNAL("accepted()"), self.doUpload)            
                
    # Managing the upload queue.
    def doUpload(self):
        #upload the file.
        self.threadPool.append(GenericThread(self.doRealUpload))
        self.disconnect(self, QtCore.SIGNAL("doneUpload(QString)"), self.doneUpload)
        self.connect(self, QtCore.SIGNAL("doneUpload(QString)"), self.doneUpload)
        self.threadPool[len(self.threadPool) - 1].start()
        self.setFocus()
    
    # Do the upload.
    def doRealUpload(self):        
        # Get the video's info.
        video_location = self.uploadDialog.lineEditFilePath.text()
        video_title = self.uploadDialog.lineEditVideoName.text()
        tags = self.uploadDialog.lineEditTags.text()
        description = self.uploadDialog.plainTextEditDescription.toPlainText()
        
        try:
            yt_service = self.getYouTubeService()
            yt_service.DirectVideoUpload(self, video_title, description, tags, video_location)
            self.emit(QtCore.SIGNAL('doneUpload(QString)'), QtCore.QString('Title: ' + video_title + '\nPath: ' + video_location))
        except:
            self.emit(QtCore.SIGNAL('uploadFailed(Qstring)'), QtCore.QString('^(^$(^(^(^('))
        
    # A message notifying upload sucessfully event.
    def doneUpload(self, message):
        messageDialog = WarningDialog.WarningDialog("The video % has been successfully uploaded." % str(message))
        messageDialog.show()
        
    # Display youtube feeds
    
    @QtCore.pyqtSlot()
    def on_btnTopRated_clicked(self):
        self.searchFeed("topRated")
    
    @QtCore.pyqtSlot()
    def on_btnTopFavorites_clicked(self):
        self.searchFeed("topFavorites")
        
    @QtCore.pyqtSlot()
    def on_btnMostShared_clicked(self):
        self.searchFeed("mostShared")
                
    @QtCore.pyqtSlot()
    def on_btnMostPopular_clicked(self):
        self.searchFeed("mostPopular")
    
    @QtCore.pyqtSlot()
    def on_btnMostRecent_clicked(self):
        self.searchFeed("mostRecent")
    
    @QtCore.pyqtSlot()
    def on_btnMostDiscussed_clicked(self):
        self.searchFeed("mostDiscussed")
    
    @QtCore.pyqtSlot()
    def on_btnMostResponded_clicked(self):
        self.searchFeed("mostResponded")
            
    @QtCore.pyqtSlot()
    def on_btnRecentlyFeatured_clicked(self):
        self.searchFeed("recentlyFeatured")
    
    @QtCore.pyqtSlot()
    def on_btnTrending_clicked(self):
        self.searchFeed("trending")
    
    # Search a feed of given name.
    def searchFeed(self, feedName):
        print "Searching", feedName
        # Create a thread to do the search.
        self.threadPool.append(GenericThread(self.ytFeedSearch, feedName))   
        self.disconnect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.connect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.threadPool[len(self.threadPool) - 1].start()
        self.setFocus()
    
    def ytFeedSearch(self, feedName):
        yt_service = self.getYouTubeService()
        if feedName == 'topRated':
            feed = yt_service.RetrieveTopRatedVideoFeed()
        elif feedName == "topFavorites":
            feed = yt_service.RetrieveTopFavoritesVideoFeed()
        elif feedName == "mostShared":
            feed = yt_service.client.GetYouTubeVideoFeed("https://gdata.youtube.com/feeds/api/standardfeeds/most_shared")
        elif feedName == "mostPopular":
            feed = yt_service.client.GetYouTubeVideoFeed("https://gdata.youtube.com/feeds/api/standardfeeds/most_popular")
        elif feedName == "mostRecent":
            feed = yt_service.RetrieveMostRecentVideoFeed()
        elif feedName == "mostDiscussed":
            feed = yt_service.RetrieveMostDiscussedVideoFeed()
        elif feedName == "mostResponded":
            feed = yt_service.RetrieveostRespondedVideoFeed()
        elif feedName == 'recentlyFeatured':
            feed = yt_service.RetrieveRecentlyFeaturedVideoFeed()      
        elif feedName == "trending":
            feed = yt_service.client.GetYouTubeVideoFeed("https://gdata.youtube.com/feeds/api/standardfeeds/on_the_web")
        else:
            feed = None
            print 'Invalid feed'            
        print "Done searching"
        
        html = getHtmlFromFeed.getHtmlFeedDescription(feed)
        print "html: " + html
        self.emit(QtCore.SIGNAL('doneSearching(QString)'), html)
    
    def login(self, email, password):
        try:
            self.yt_service = YouTubeService(email, password)
            self.logged_in = True
            self.emit(QtCore.SIGNAL("doneLogin(QString)"), email)
        except:
            print "Failed!"
            self.emit(QtCore.SIGNAL("failedLogin()"))
        
    # User clicked on the 'login' button.
    @QtCore.pyqtSlot()
    def on_btnLogin_clicked(self):
        # Start a login thread.
        username = self.ledUsername.text()
        password = self.ledPassword.text()
        
        self.threadPool.append(GenericThread(self.login, username, password))
        self.disconnect(self, QtCore.SIGNAL("doneLogin(QString)"), self.setUsernameView)
        self.connect(self, QtCore.SIGNAL("doneLogin(QString)"), self.setUsernameView)
        self.disconnect(self, QtCore.SIGNAL("failedLogin()"), self.failedLoginWarning)
        self.connect(self, QtCore.SIGNAL("failedLogin()"), self.failedLoginWarning)
        self.threadPool[len(self.threadPool) - 1].start()
        self.setFocus()
               
    
    #
    def setUsernameView(self, username):
        self.labelGreeting.setText("Hello, %s" % username)
        
    def failedLoginWarning(self):
        print "Sorry, login failed!" 
        warningDialog = WarningDialog.WarningDialog(warning="Sorry, logging in failed", parent=self)
        warningDialog.show()
               
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Simple player')

    # Create a UI instance.
    videoPlayer = VideoPlayer()

    # Show the UI.
    videoPlayer.show()
    app.exec_()

