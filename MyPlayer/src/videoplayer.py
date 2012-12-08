# -*- coding: utf-8 *-*
###############################################################################
# A simple media player.
# This project is based on the tutorial
#
#
#

import traceback
import sys
import random
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtWebKit import QWebPage, QWebSettings

import gdata.youtube.service

# Two additional UI module.
import about
import print_entry

from QtThread import GenericThread
from login_youtube import doLogin

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
        self.repeat = False # Default mode: not repeating the play list.
        
        # The dock widget: show or hide?
        self.dckShown = True
        self.lineEditSearch.setFocus()   
        
        # Search thread.
        self.threadPool = []
        
        # The threads that process an Youtube link to get direct links.
        self.ytGetDirectLinkPool = []
        
        # The thread that search for a feed.
        self.searchFeedPool = []
        
        # Enable the flash plugin
        QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
        
        # Search box: Enter pressed.
        self.lineEditSearch.returnPressed.connect(self.on_btnSearchVideo_clicked)
        
        # The page showing search result.
        self.videoList.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.videoList.connect(self.videoList, QtCore.SIGNAL('linkClicked(const QUrl&)'), self.linkClicked)
        
        # Load the page for Youtube.
        self.stackedWidget.setCurrentIndex(1)
        
        #The id of this application and the place to login.
        self.clientId = '401858455989.apps.googleusercontent.com'
        self.clientSecret = 'qs1g3M6c2YvD9CCiMHIeClOy'
        self.homeURL = QtCore.QUrl(r'https://youtube.com')
        
        #Load the default page.
        self.videoList.load(self.homeURL)
        
        if not self.videoList.page().networkAccessManager() == None:
            print "Now the two page should share the same session!"
            self.playerView.page().setNetworkAccessManager(self.videoList.page().networkAccessManager())
            self.accountTask.page().setNetworkAccessManager(self.videoList.page().networkAccessManager())

        # A seperate frame for login.
        self.logged_in = False
    
    # Click a link in the list of videos.
    def linkClicked(self, url):
        print "You clicked on a link", url.toString()
        if str(url.toString()).find('youtube') != -1:
            self.addMedia(url)
    
    #Click on the 'search' button in the search tab.
    @QtCore.pyqtSlot()
    def on_btnSearchVideo_clicked(self):
        # Get the order option.
        if self.lineEditSearch.text() == '':
            return    
        if self.rdbRelevance.isChecked():
            order = "relevance"
        elif self.rdbPublished.isChecked():
            order = "published"
        elif self.rdbView.isChecked():
            order = "viewCount"
        else:
            order = "rating"
        
        # Get the safe search option.
        if self.rdbSafeNone.isChecked():
            safe = "none"
        elif self.rdbSafeModerate.isChecked():
            safe = "moderate"
        else:
            safe = "strict"
        
        # searching not done: Print the defaul message.
        self.videoList.setHtml("<html><body><h1>Searching ...</h1></body></html>")
        
        # Create a thread to do the search.
        self.threadPool.append(GenericThread(self.ytSearch, order, safe, self.lineEditSearch.text()))        
        self.disconnect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.connect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.threadPool[len(self.threadPool) - 1].start()
        self.setFocus()
        
    def setHtml(self, html):
        print "Setting html"
        self.videoList.setHtml(html)
        
    def ytSearch(self, order, safe, vq):
        try:
            # Init service.
            yt_service = gdata.youtube.service.YouTubeService()
            
            # Init search query.
            query = gdata.youtube.service.YouTubeVideoQuery()    
            query.orderby = order
            query.safeSearch = safe
            query.vq = str(vq)
            
            # Run the query.
            feed = yt_service.YouTubeQuery(query)            
        except:
            pass
        html = self.getFeedHtml(feed)
        self.emit(QtCore.SIGNAL('doneSearching(QString)'), html)
    
    def getFeedHtml(self, feed):
        html = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title>Search Result</title></head><body><ol>'
        try:
            for entry in feed.entry:
                html += "<li>%s</li>" % print_entry.getHtmlEntry(entry)
        except:
            html += '<font color="red">Getting search result: Error'
        html += "</ol></body></html>"
        
        return html               

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

    # Event: The 'Full screen' button is clicked.
    # Switch between 'normal' mode and 'full screen' mode.
    @QtCore.pyqtSlot()
    def on_btnFullscreen_clicked(self):
        if self.isFullScreen():
            # switch to normal mode.
            self.showNormal()
            # show the play list.
            self.dckPlayList.show()
        else:
            # Switch to full screen mode.
            self.showFullScreen()
            # Hide the play list.
            self.dckPlayList.hide()
            # Hide the mouse cursor.
            self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

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
        print "link:", link
        
        #Switch to the playerPage
        #Play the selected video.
        print "Switching to the video page"
        self.stackedWidget.setCurrentIndex(0)
        print "Loading", link.toString()
        self.playerView.load(link)
        print 'Adding Url: Done'

    # Add to the play a link
    def addMedia(self, url):
        print 'Running: Add Media'
        self.playlist.append(url)

        # update the play list.
        self.updatePlayList()

        # If the play list has been loaded and there isn't a media playing,
        # play it.
        if len(self.playlist) == 1:
            self.stackedWidget.setCurrentIndex(0)
            print "Now playing", url.toString()
            self.playerView.load(url)
        
        
    # Update the play list.
    def updatePlayList(self):
        # Remove all items in QListWidget
        self.lswPlaylist.clear()

        # add the new play list.
        for item in self.playlist:
            self.lswPlaylist.addItem(item.toString())


    
    # mouseDoubleClickEvent is a protected method which called when user
    # double clicks in the GUI and this event isn't caught by any other widget.
    def mouseDoubleClickEvent(self, event):
        # Always, before process the event, we must send a copy of it to the
        # ancestor class.
        QtGui.QMainWindow.mouseDoubleClickEvent(self, event)

        # Go to full-screen mode or exit from it.
        self.on_btnFullscreen_clicked()
    
    
    # Select the page vie: Search result of video page.
    @QtCore.pyqtSlot()
    def on_showVideoPage_clicked(self):
        self.stackedWidget.setCurrentIndex(0)
    
    # Ask to navigate to search result page.
    @QtCore.pyqtSlot()
    def on_showSearchPage_clicked(self):
        self.stackedWidget.setCurrentIndex(2)
    
    
    # Ask to navigate to account page.
    @QtCore.pyqtSlot()
    def on_showAccountPage_clicked(self):
        self.stackedWidget.setCurrentIndex(1)
        
    @QtCore.pyqtSlot()
    def on_btnUpload_clicked(self):
        if not self.logged_in:
            print "You have to login first"
        else:
            self.accountTask.load(QtCore.QUrl("https://www.youtube.com/my_videos_upload"))
            self.on_showAccountPage_clicked()
    
    # Display youtube feeds
    @QtCore.pyqtSlot()
    def on_btnMostViewed_clicked(self):
        self.searchFeed("mostViewed")
    
    @QtCore.pyqtSlot()
    def on_btnTopRated_clicked(self):
        self.searchFeed("topRated")
    @QtCore.pyqtSlot()
    def on_btnRecentlyFeatured_clicked(self):
        self.searchFeed("recentlyFeatured")
    @QtCore.pyqtSlot()
    def on_btnMostDiscussed_clicked(self):
        self.searchFeed("mostDiscussed")
    @QtCore.pyqtSlot()
    def on_btnTopFavorites_clicked(self):
        self.searchFeed("topFavorites")
    @QtCore.pyqtSlot()
    def on_btnMostLinked_clicked(self):
        self.searchFeed("mostLinked")
    @QtCore.pyqtSlot()
    def on_btnMostResponded_clicked(self):
        self.searchFeed("mostResponded")
    @QtCore.pyqtSlot()
    def on_btnMostRecent_clicked(self):
        self.searchFeed("mostRecent")
        
    def searchFeed(self, feedName):
        print "You want to search the feed", feedName
        
        # Create a thread to do the search.
        self.searchFeedPool.append(GenericThread(self.ytFeedSearch, feedName))   
        self.disconnect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.connect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.searchFeedPool[len(self.searchFeedPool) - 1].start()
        self.setFocus()
    
    def ytFeedSearch(self, feedName):
        yt_service = gdata.youtube.service.YouTubeService()
        if feedName == "mostViewed":
            feed = yt_service.GetMostViewedVideoFeed()
        elif feedName == 'topRated':
            feed = yt_service.GetTopRatedVideoFeed()
        elif feedName == 'recentlyFeatured':
            feed = yt_service.GetRecentlyFeaturedVideoFeed()
        elif feedName == "mostDiscussed":
            feed = yt_service.GetMostDiscussedVideoFeed()
        elif feedName == "topFavorites":
            feed = yt_service.GetTopFavoritesVideoFeed()
        elif feedName == "mostLinked":
            feed = yt_service.GetMostLinkedVideoFeed()
        elif feedName == "mostResponded":
            feed = yt_service.GetMostRespondedVideoFeed()
        else:
            feed = yt_service.GetMostRecentVideoFeed()
        
        html = self.getFeedHtml(feed)
        self.emit(QtCore.SIGNAL('doneSearching(QString)'), html)
    
    def login(self, email, password):
        # This takes time, so we have to start a thread.
        print "Starting youtube service"
        yt_service = gdata.youtube.service.YouTubeService()
        yt_service.email = email
        yt_service.password = password
        print "Setting username and password: done"
        
        # Login.
        try:
            # API: login.
            print "Call ProgrammaticLogin()"
            print yt_service.ProgrammaticLogin()
            print "After the call"            
        except:
            #TODO: Display a warning dialog.
            print "Login failed!"
            self.logged_in = False
            self.emit(QtCore.SIGNAL('failedLogin()'))
            return
        print "setting logged_in = True"
        self.logged_in = True
        self.emit(QtCore.SIGNAL('doneLogin(QString)'), QtCore.QString(email + " " + password))
    
    
    # User clicked on the 'login' button.
    @QtCore.pyqtSlot()
    def on_btnLogin_clicked(self):
        print "The 'Loggin button '"     
        if not self.logged_in:
            print "Start the login process"
            
            # Start a login thread.
            username = self.ledUsername.text()
            password = self.ledPassword.text()
            loginThread = GenericThread(self.login, username, password)
            self.connect(self, QtCore.SIGNAL("doneLogin(QString)"), self.webLogin)
            self.connect(self, QtCore.SIGNAL("failedLogin()"), self.failedLoginWarning)
            print "The login thread is started"
            loginThread.start()       
        
    def webLogin(self, loginInfo):
        #Web login.
        #Load the login page and fill in information.
        [username, password] = str(loginInfo).split()
        doLogin(self.accountTask, QtCore.QUrl(r"https://accounts.google.com/Login"), username, password)
        self.labelGreeting.setText("Hello, %s" % username)
            
        # Load the login page and log in using the web interface.
        self.videoList.load(self.homeURL)
        
    def failedLoginWarning(self):
        #TODO: display a warning message.
        print "Login failed."
            
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Simple player')

    # Create a UI instance.
    videoPlayer = VideoPlayer()

    # Show the UI.
    videoPlayer.show()
    app.exec_()

