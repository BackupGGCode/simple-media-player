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

# Two additional UI module.
import about

from QtThread import GenericThread
from uploadDialog import UploadDialog
import WarningDialog
from YoutubeService import YouTubeService
from getHtmlFromFeed import getHtmlFeedDescription
import getHtmlFromFeed
from searchOption import SearchOptionDialog

# A class represent a simple media player.
class VideoPlayer(QtGui.QMainWindow):

    def __init__(self):
        # Initialize: calling the inherited __init__ function.
        super(VideoPlayer, self).__init__()
        
        # Load the defined UI.
        uic.loadUi('../share/ui/new_ui.ui', self)
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
        
        # Search box: Enter pressed.
        self.lineEditSearch.returnPressed.connect(self.on_btnSearchVideo_clicked)
        
        # The page showing search result.
        # Enable the flash plugin
        QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
        self.videoList.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.videoList.connect(self.videoList, QtCore.SIGNAL('linkClicked(const QUrl&)'), self.linkClicked)

        # A seperate frame for login.
        self.logged_in = False
        self.yt_service = None
        
        # A list of uploading video.
        self.uploadingList = []
        self.uploadDialog = UploadDialog(self)
        self.downloadingList = []
        
        self.feed = None # The current feed, displayed on the search result page.
        self.entry = None # The current entry, playing.
        
        # Advance search options
        self.advancedSearchDialog = SearchOptionDialog(parent = self)
        self.connect(self.advancedSearchDialog.optionDialogSearchTerm, QtCore.SIGNAL("returnPressed()"), self.advancedSearch)
        self.connect(self.advancedSearchDialog.lineeditUserFeed, QtCore.SIGNAL("returnPressed()"), self.on_lineeditUserFeed_returnPressed)
        
        self.connect(self.advancedSearchDialog.btnTrending , QtCore.SIGNAL("clicked()"), self.on_btnTrending_clicked)
        self.connect(self.advancedSearchDialog.btnTopRated , QtCore.SIGNAL("clicked()"), self.on_btnTopRated_clicked)
        self.connect(self.advancedSearchDialog.btnRecentlyFeatured , QtCore.SIGNAL("clicked()"), self.on_btnRecentlyFeatured_clicked)
        self.connect(self.advancedSearchDialog.btnTopFavorites , QtCore.SIGNAL("clicked()"), self.on_btnTopFavorites_clicked)
        self.connect(self.advancedSearchDialog.btnMostShared , QtCore.SIGNAL("clicked()"), self.on_btnMostShared_clicked)
        self.connect(self.advancedSearchDialog.btnMostResponded , QtCore.SIGNAL("clicked()"), self.on_btnMostResponded_clicked)
        self.connect(self.advancedSearchDialog.btnMostDiscussed , QtCore.SIGNAL("clicked()"), self.on_btnMostDiscussed_clicked)
        self.connect(self.advancedSearchDialog.btnMostRecent , QtCore.SIGNAL("clicked()"), self.on_btnMostRecent_clicked)
        self.connect(self.advancedSearchDialog.btnMostPopular , QtCore.SIGNAL("clicked()"), self.on_btnMostPopular_clicked)        
    
    def getAdvancedSearchOptions(self):
        vq = str(self.advancedSearchDialog.optionDialogSearchTerm.text())
        results_number = self.advancedSearchDialog.spbMaxResults.count()
        sort_by = str(self.advancedSearchDialog.optionDialogSortby.text()).lower()
        _format = int(str(self.advancedSearchDialog.optionDialogFormat.text())[:2])
        safe = str(self.advancedSearchDialog.optionDialogSafeSearch.text()).lower()
        genre = int(str(self.advancedSearchDialog.optionDialogGenre.text())[:2])
        
        return [vq, sort_by, safe, genre, results_number]
    
    def advancedSearch(self):
        self.advancedSearchDialog.optionDialogSearchTerm.selectAll()
        
    # Click a link in the list of videos.
    def linkClicked(self, url):
        print url
        tmp = None
        # Find the entry that has that url.
        if (self.feed == None):
            print "($&(Q&$(&!(&(!&(&ERROR"
        else:
            for  entry in self.feed.entry:
                #print  entry.GetSwfUrl()
                if entry.GetSwfUrl() == str(url.toString()):
                    tmp = entry
                    break
                    
        print "Tmp's links: ", tmp.GetSwfUrl()
        self.addMedia(tmp)
    
    def startThread(self, function, signal_ok, signal_fail, function_if_ok, function_if_fail, *args):
        self.threadPool.append(GenericThread(function, *args))
        self.disconnect(self, signal_ok, function_if_ok)
        self.connect(self, signal_ok, function_if_ok)
        self.disconnect(self, signal_fail, function_if_fail)
        self.connect(self, signal_fail, function_if_fail)
        self.threadPool[len(self.threadPool) - 1].start()
        self.setFocus()
    
    def dummy(self):
        print 'This function do nothing'
    
    # User's feed.
    @QtCore.pyqtSlot()
    def on_lineeditUserFeed_returnPressed(self):
        # Start a thread for searching.
        self.advancedSearchDialog.lineeditUserFeed
        self.startThread(self.ytUserFeedSearch,
                         QtCore.SIGNAL("doneSearching(QString)"), 
                         QtCore.SIGNAL("searchFailed()"), 
                         self.setHtml, 
                         self.dummy,
                         str(self.advancedSearchDialog.lineeditUserFeed.displayText()))        
    
    # Return an instance that helps us to use youtube's services.
    def getYouTubeService(self, username='', password=''):
        if (username != '' and password != ''): # new instance.
                self.yt_service = YouTubeService(username, password)
                return self.yt_service
        elif self.yt_service != None:
            return self.yt_service
        else:
            self.yt_service = YouTubeService()
            return self.yt_service
    
    def ytUserFeedSearch(self, username):
        try:
            yt_service = self.getYouTubeService()
            feed = yt_service.RetrieveUserVideosbyUsername(username)
            html = getHtmlFeedDescription(feed)
        except:
            html = "Sorry, no such user."
            feed = None
        
        self.feed = feed        
        self.emit(QtCore.SIGNAL('doneSearching(QString)'), QtCore.QString(html))
            
    # Click on the Search options button.
    @QtCore.pyqtSlot()
    def on_btnSearchOption_clicked(self):
        self.advancedSearchDialog.show()
        self.advancedSearchDialog.setFocus()
    
    #Click on the 'search' button in the search tab.
    @QtCore.pyqtSlot()
    def on_btnSearchVideo_clicked(self):
        # Get the order option.
        if self.lineEditSearch.text() == '':
            return    
        
        # get the search term.
        vq = str(self.lineEditSearch.text())
        
        # searching not done: Print the defaul message.
        self.videoList.setHtml("<html><body><h1>Searching ...</h1></body></html>")
        
        # Create a thread to do the search.
        self.startThread(self.ytSearch, 
                         QtCore.SIGNAL("doneSearching(QString)"), 
                         QtCore.SIGNAL("searchFailed()"), 
                         self.setHtml,
                         self.dummy,
                         vq, 'relevance', 'include', 40)        
    
    # Set the content of the playlist page.
    def setHtml(self, html):
        self.videoList.setHtml(html)
        self.twgWebpage.setCurrentIndex(1)
    
    # Do the search.
    #TODO Re-implement using YoutubeService.
    def ytSearch(self, vq, orderby, racy, max_results):
        try:
            # Init service.
            yt_service = self.getYouTubeService()
            #vq must be converted to str.
            feed = yt_service.SearchWithVideoQuery(str(vq), orderby, racy, max_results)
        except:
            feed = None
        self.feed = feed
        html = getHtmlFeedDescription(feed)
        self.emit(QtCore.SIGNAL('doneSearching(QString)'), html)

    # Event: The 'About' button is clicked
    # Show the about dialog.
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
        print "A link is clicked!"
        # If the play list is empty, do nothing.
        if self.playlist == []:
            return
        
        # Get the index of model_index, use it to obtain corresponding link
        link = self.playlist[self.lswPlaylist.currentRow()].GetSwfUrl();
        
        #Switch to the playerPage
        #Play the selected video.
        self.twgWebpage.setCurrentIndex(0)
        html = '<embed src="%s" type="application/x-shockwave-flash" allowfullscreen="true" width="640" height="480"></embed>' % link
        print html
        self.playerView.setHtml(html)

    # Add to the play a link
    # Url must be a string.
    def addMedia(self, entry):
        print "Adding media to playlist."
        self.playlist.append(entry)

        # update the play list.
        self.updatePlayList()

        # If the play list has been loaded and there isn't a media playing,
        # play it.
        if len(self.playlist) == 1:
            print "Starting the play"
            self.entry = entry
            self.twgWebpage.setCurrentIndex(0)
            self.playerView.setHtml(QtCore.QString(self._htmlForFlash(entry.GetSwfUrl())))
        
    # Update the play list.
    def updatePlayList(self):
        # Remove all items in QListWidget
        self.lswPlaylist.clear()

        # add the new play list.
        for item in self.playlist:
            self.lswPlaylist.addItem(QtCore.QString(unicode(item.media.title.text)))
        
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
        print "Inside the function doUpload"
        #upload the file.
        self.startThread(self.doRealUpload, 
                         QtCore.SIGNAL("doneUpload(QString)"),
                         QtCore.SIGNAL('uploadFailed(Qstring)'),
                         self.doneUpload, 
                         self.uploadFailed)
    
    # Do the upload.
    def doRealUpload(self):        
        # Get the video's info.
        video_location = str(self.uploadDialog.lineEditFilePath.text())
        video_title = str(self.uploadDialog.lineEditVideoName.text())
        tags = str(self.uploadDialog.lineEditTags.text())
        description = str(self.uploadDialog.plainTextEditDescription.toPlainText())
        
        # This will work on Windows only.
        video_location = video_location.replace('/', '\\')
        print video_location, type(video_location)
        print video_title, type(video_title)
        print tags, type(tags)
        print description, type(description)
        
        try:
            self.getYouTubeService()
            self.yt_service.DirectVideoUpload(video_title, description, tags, video_location)
            self.emit(QtCore.SIGNAL('doneUpload(QString)'), QtCore.QString("done upload!"))
        except:
            self.emit(QtCore.SIGNAL('uploadFailed(Qstring)'), QtCore.QString('^(^$(^(^(^('))
        
    # A message notifying upload sucessfully event.
    def doneUpload(self, message):
        messageDialog = WarningDialog.WarningDialog("The video %s has been successfully uploaded." % str(message))
        messageDialog.show()
    def uploadFailed(self, message):
        messageDialog = WarningDialog.WarningDialog("Upload failed: %s" %str(message))
        messageDialog.show()
        
    # Search for popular feeds.
    def on_btnTopRated_clicked(self):
        self.searchFeed("topRated")
    
    def on_btnTopFavorites_clicked(self):
        self.searchFeed("topFavorites")
        
    def on_btnMostShared_clicked(self):
        self.searchFeed("mostShared")
                
    def on_btnMostPopular_clicked(self):
        self.searchFeed("mostPopular")
    
    def on_btnMostRecent_clicked(self):
        self.searchFeed("mostRecent")
    
    def on_btnMostDiscussed_clicked(self):
        self.searchFeed("mostDiscussed")
    
    def on_btnMostResponded_clicked(self):
        self.searchFeed("mostResponded")
            
    def on_btnRecentlyFeatured_clicked(self):
        self.searchFeed("recentlyFeatured")
    
    def on_btnTrending_clicked(self):
        self.searchFeed("trending")
    
    # Search a feed of given name.
    def searchFeed(self, feedName):
        print "Searching", feedName
        # Create a thread to do the search.
        self.startThread(self.ytFeedSearch, 
                         QtCore.SIGNAL("doneSearching(QString)"),
                         QtCore.SIGNAL("failedSearching(QString)"),
                         self.setHtml,
                         self.dummy,
                         feedName)
    
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
        
        self.feed = feed
        html = getHtmlFromFeed.getHtmlFeedDescription(feed)
        self.emit(QtCore.SIGNAL('doneSearching(QString)'), html)
    
    def login(self, email, password):
        print "Inside the login function"
        print email, type(email)
        try:
            self.yt_service = YouTubeService(email, password)
            self.logged_in = self.yt_service.loggedIn
            if (self.logged_in):
                self.emit(QtCore.SIGNAL("doneLogin(QString)"), email)
            else:
                print "Failed!"
                self.emit(QtCore.SIGNAL("failedLogin()"))
        except:
            print "Failed!"
            self.emit(QtCore.SIGNAL("failedLogin()"))
            
    
    #User clicked on the 
    @QtCore.pyqtSlot()
    def on_btnPost_clicked(self):
        print "Post comments here."
    
    @QtCore.pyqtSlot()
    def on_btnRate_clicked(self):
        print "Rate the current video here!"
    
    @QtCore.pyqtSlot()
    def on_btnSelectToPlay_clicked(self):
        print "Choose media numbers and add to play list."
    @QtCore.pyqtSlot()
    def on_btnSelectToDownload_clicked(self):
        print "Choosing media to download."
        
    # User clicked on the 'login' button.
    @QtCore.pyqtSlot()
    def on_btnLogin_clicked(self):
        # Start a login thread.
        username = str(self.ledUsername.text())
        password = str(self.ledPassword.text())
        
        self.startThread(self.login,
                         QtCore.SIGNAL("doneLogin(QString)"),
                         QtCore.SIGNAL("failedLogin()"),
                        self.setUsernameView,
                        self.failedLoginWarning,
                        username, password)
    
    # Show the username.
    def setUsernameView(self, username):
        self.labelGreeting.setText("Hello, %s" % username)
        
    def failedLoginWarning(self):
        print "Sorry, login failed!" 
        warningDialog = WarningDialog.WarningDialog(warning="Sorry, logging in failed", parent=self)
        warningDialog.show()
    
    def _htmlForFlash(self, url):
        html = ''''<embed src="%s" type="application/x-shockwave-flash" allowfullscreen="true" width="640" height="480"></embed>
        ''' % url
        
        return html
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Simple player')

    # Create a UI instance.
    videoPlayer = VideoPlayer()

    # Show the UI.
    videoPlayer.show()
    app.exec_()

