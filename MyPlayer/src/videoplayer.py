# -*- coding: utf-8 *-*
###############################################################################
# A simple media player.
#
#
#

import sys
import random
from PyQt4 import QtCore, QtGui, uic, phonon
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
from print_entry import getVideoId
from upload_status import UploadStatusDialog
import time
import webbrowser
import pickle
import gdata
from youtube_dl_wrapper import YouTubeDl
import subprocess
from subprocess import Popen
import re

# A class represent a simple media player.
class VideoPlayer(QtGui.QMainWindow):

    def __init__(self):
        # Initialize: calling the inherited __init__ function.
        super(VideoPlayer, self).__init__()
        
        # Load the defined UI.
        uic.loadUi('../share/ui/new_ui.ui', self)
        self.initAttributes()           

################################################################################################
# Initialize class attributes.
################################################################################################
    def initAttributes(self):
        self.showMaximized()

        # Initialize the play list.
        self.playlist = []  # A list of links to the file to play.
        self.playlistTmp = []  # A temporary play list, use to shuffle play list.
        self.repeat = False
        
        # A timer showing the playing time.
        self.tmrTimer = QtCore.QTimer(self)
        self.tmrTimer.setInterval(250) # This will emit a signal every 1/4 second
        self.tmrTimer.timeout.connect(self.on_tmrTimer_timeout)
        self.tmrTimer.start()
        
        #Volume control.
        self.sldVolumeSlider.setAudioOutput(self.vdpVideo.audioOutput())
        self.sldSeekSlider.setMediaObject(self.vdpVideo.mediaObject())        
        
        
        # initialize the current mouse position and time.
        self.mousePos0 = QtGui.QCursor.pos()
        self.mouseT0 = QtCore.QTime.currentTime()
        
        # The dock widget: show or hide?
        self.dckShown = True
        self.lineEditSearch.setFocus()   
        
        
        # A list of uploading video.
        self.uploadingList = {}
        self.uploadDialog = UploadDialog(self)
        self.downloadingList = []

        self.feed = None  # The current feed, displayed on the search result page.
        self.entry = None  # The current entry, playing.
        self.currentDirectLink = "" # Direct link to the current video.
        self.currentVideo = None
        
        
        # The dock widget: show or hide?
        self.dckShown = True
        self.lineEditSearch.setFocus()   
        
        # Search thread.
        self.threadPool = []
        self.threadType = []  # Store the function names that run as threads in self.threadPool.
        
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
        
        # Advance search options
        self.advancedSearchDialog = SearchOptionDialog(parent=self)
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
    
        # Menu bar actions.
        self.action_Save_playlist.triggered.connect(self.on_action_Save_playlist)
        self.action_Load_playlist.triggered.connect(self.on_action_Load_playlist)
        self.action_Open_download_folder.triggered.connect(self.on_action_Open_download_folder)
        self.action_Quit.triggered.connect(self.on_action_Quit)
        self.action_Guide.triggered.connect(self.on_action_Guide)
        self.action_About.triggered.connect(self.on_action_About)
        self.actionS_earch_option.triggered.connect(self.on_actionS_earch_option)
        
        self.vdpVideo.finished.connect(self.on_btnNext_clicked)
        
        self.btnLogout.setEnabled(False)
        
        self.connect(self, QtCore.SIGNAL("IWantToBeNoticed(QString)"), self.showMessage) 

################################################################################################
# Actions related to playlist
################################################################################################     
    # Some menu action.
    def on_action_Save_playlist(self):
        if self.playlist is None or len(self.playlist) == 0:
            warning = WarningDialog.WarningDialog("There is nothing to save!", self)
            warning.show()
        else:
            # Create a dialog showing the place to save the playlist.
            file_types = "Playlist (*.playlist);; All file (*.*)"
            filename, _ = QtGui.QFileDialog.getSaveFileNameAndFilter(self, QtCore.QString("Save play list"), '', file_types)
            filename = unicode(filename.__str__())
            try:
                # save the playlist.
                playlist_file = open(filename, 'wb')
                pickle.dump(self.playlist, playlist_file)
                playlist_file.close()
                print "The play list is saved."
            except:
                warning = WarningDialog.WarningDialog("Sorry, the play list cannot be saved!", self)
                warning.show()
    
    def on_action_Load_playlist(self):
        # Create a file dialog to load the playlist.
        file_types = "Playlist (*.playlist);; All file (*.*)"
        filename, _ = QtGui.QFileDialog.getOpenFileNameAndFilter(self, QtCore.QString("Load play list"), '', file_types)
        filename = unicode(filename.__str__())
        
        playlist_file = open(filename, 'rb')
        temp_playlist = pickle.load(playlist_file)
        if temp_playlist is None or not isinstance(temp_playlist, list):
            raise ValueError
        self.playlist = []
        for entry in temp_playlist:
            # Check the validity of the entry.
            if isinstance(entry, gdata.youtube.YouTubeVideoEntry):
                self.playlist.append(entry)
            # update the playlist.
        self.updatePlayList()
        # except:
        #    warning = WarningDialog.WarningDialog("Sorry, the play list cannot be loaded!", self)
        #    warning.show()
        # finally:
        playlist_file.close()
        
    # Event: The next button is pressed.
    @QtCore.pyqtSlot()
    def on_btnNext_clicked(self):
        print "The next button is clicked."
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
        
    def updatePlayList(self):
        currentRow = self.lswPlaylist.currentRow()
        # Remove all items in QListWidget
        self.lswPlaylist.clear()
        # add the new play list.
        for item in self.playlist:
            self.lswPlaylist.addItem(QtCore.QString(unicode(item.media.title.text)))
        self.lswPlaylist.setCurrentRow(currentRow)
    
    

    # Action: Double an item in the play list to play it.
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_lswPlaylist_doubleClicked(self):
        # If the play list is empty, do nothing.
        if self.playlist == []:
            return
        
        # Get the index of model_index, use it to obtain corresponding link
        self.entry = self.playlist[self.lswPlaylist.currentRow()]
        
        # Switch to the playerPage
        # Play the selected video.
        print "Processing the link,", self.entry.media.player.url
        self.startThread(self.getYoutubeLinkToPlay, QtCore.SIGNAL("doneGetDirectLinks(QString)"), QtCore.SIGNAL("failedGetDirectLinks(QString)"), self.playVideo, self.dummy, self.entry.media.player.url)

################################################################################################
# Action related tp main menu.
################################################################################################
    def on_action_Open_download_folder(self):
        print "Open download folder here."
    
    def on_action_Quit(self):
        self.close()
        
    def on_actionS_earch_option(self):
        print "Setting search option here!"
        
    def on_action_Guide(self):
        webbrowser.open(r'https://code.google.com/p/simple-media-player/w/list')
        
    def on_action_About(self):
        aboutDialog = about.About(parent=self)
        aboutDialog.show()

################################################################################################
# Search
################################################################################################        
    def getAdvancedSearchOptions(self):
        vq = str(self.advancedSearchDialog.optionDialogSearchTerm.text())
        author = str(self.advancedSearchDialog.lineeditUserFeed.text())
        results_number = self.advancedSearchDialog.spbMaxResults.value()
        sort_by = str(self.advancedSearchDialog.optionDialogSortby.currentText()).lower()
        
        # Change to standard name.
        if sort_by == 'published date':
            sort_by = 'published'
        elif sort_by == 'view count':
            sort_by = 'viewCount'
            
        racy = str(self.advancedSearchDialog.optionDialogSafeSearch.currentText()).lower()
        startIndex = self.advancedSearchDialog.spbStartIndex.value()
        time = str(self.advancedSearchDialog.cbTime.currentText()).lower()
        
        return [vq, author, results_number, sort_by, racy, startIndex, time]
    
    
    # User's feed.
    @QtCore.pyqtSlot()
    def on_lineeditUserFeed_returnPressed(self):
        # Start a thread for searching.
        self.advancedSearchDialog.lineeditUserFeed
        self.startThread(self.ytUserFeedSearch,
                         QtCore.SIGNAL("doneSearching(QString)"),
                         QtCore.SIGNAL("searchFailed()"),
                         self.setHtml,
                         self.dummy)        
    
    # Return an instance that helps us to use youtube's services.
    def getYouTubeService(self, username='', password=''):
        if (username != '' and password != ''):  # new instance.
                self.yt_service = YouTubeService(username, password)
                return self.yt_service
        elif self.yt_service != None:
            return self.yt_service
        else:
            self.yt_service = YouTubeService()
            return self.yt_service
    
    def ytUserFeedSearch(self):
        try:
            [vq, author, results_number, sort_by, racy, startIndex, time] = self.getAdvancedSearchOptions()
            print [vq, author, results_number, sort_by, racy, startIndex, time]
            yt_service = self.getYouTubeService()
            query = gdata.youtube.service.YouTubeVideoQuery()
            query.author = author
            query.max_results = results_number
            query.orderby = sort_by
            query.racy = racy
            query.start_index = startIndex
            feed = yt_service.client.YouTubeQuery(query)
      
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
    
    # Click on the 'search' button in the search tab.
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
                         vq, 'relevance', 'include', 1, 40, 'all_time')        
    
        
    # Set the content of the playlist page.
    def setHtml(self, html):
        self.videoList.setHtml(html)
        self.twgWebpage.setCurrentIndex(1)
    
    # Do the search.
    # TODO Re-implement using YoutubeService.
    def ytSearch(self, vq, orderby, racy, start_index, max_results, time):
        print "Calling ytSearch with ", [vq, orderby, racy, start_index, max_results, time]
        try:
            # Init service.
            yt_service = self.getYouTubeService()
            # vq must be converted to str.
            feed = yt_service.SearchWithVideoQuery(vq, orderby, racy, start_index, max_results, time)
        except:
            print "Something weird has occurred!"
            feed = None
        self.feed = feed
        html = getHtmlFeedDescription(feed)
        self.emit(QtCore.SIGNAL('doneSearching(QString)'), html)


    def advancedSearch(self):
        [vq, author, results_number, sort_by, racy, startIndex, time] = self.getAdvancedSearchOptions()
        # print  [vq, author, results_number, sort_by, racy,startIndex, time]
        # Create a thread to do the search.
        self.startThread(self.ytSearch,
                         QtCore.SIGNAL("doneSearching(QString)"),
                         QtCore.SIGNAL("searchFailed()"),
                         self.setHtml,
                         self.dummy,
                         vq, sort_by, racy, startIndex, results_number, time)  
        
################################################################################################
#
################################################################################################        
    # Click a link in the list of videos.
    def linkClicked(self, url):
        print url
        tmp = None
        # Find the entry that has that url.
        if (self.feed == None):
            pass
        else:
            for  entry in self.feed.entry:
                # print  entry.GetSwfUrl()
                if entry.GetSwfUrl() == str(url.toString()):
                    tmp = entry
                    break
        self.addMedia(tmp)

################################################################################################
# Functions related to threads.
################################################################################################    
    def startThread(self, function, signal_ok, signal_fail, function_if_ok, function_if_fail, *args):        
        # Connect signals and slots.
        self.disconnect(self, signal_ok, function_if_ok)
        self.connect(self, signal_ok, function_if_ok)
        self.disconnect(self, signal_fail, function_if_fail)
        self.connect(self, signal_fail, function_if_fail)
        
        # Start this thread.
        # Stop all the thread of the same type as this thread first.
        name = function.__name__.lower()
        
        # there should be only on 'search' thread.
        if name.find('search') != -1 or name == 'getyoutubelinktoplay':
            count = len(self.threadPool) - 1
            while count >= 0:
                if self.threadType[count].find('search'):
                    # Stop this thread first.
                    if self.threadPool[count].stopped():
                        print "This thread (%s) is stopped already" % count
                    else:
                        try:
                            print "Stopping thread number", count
                            self.threadPool[count].stop()
                        except:
                            pass
                    break
                count -= 1
        
        elif name.find('setplayerpage') != -1:
            # Thread of this type should not run concurrently.
            # Stop all previous thread of this type.
            count = len(self.threadPool) - 1
            while count >= 0:
                if self.threadType[count] == name:
                    # Stop this thread first.
                    if self.threadPool[count].stopped():
                        print "This thread (%s) is stopped already" % count
                    else:
                        try:
                            print "Stopping thread number", count
                            self.threadPool[count].stop()
                        except:
                            pass
                    break
                count -= 1
        
        # Update the thread pool
        self.threadPool.append(GenericThread(function, *args))
        self.threadType.append(name)
        self.threadPool[len(self.threadPool) - 1].start()
        self.setFocus()
    
    def dummy(self):
        print 'This function do nothing'


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

###################################################################################
# Video playback controls.
###################################################################################
    # Event: The 'play/pause' is pressed.
    @QtCore.pyqtSlot()
    def on_btnPlayPause_clicked(self):
        # If there is some selected item, and it is either 'playing' or
        # 'paused', then switch between the two states.
        if self.vdpVideo.isPlaying():
            print "Change to pause"
            self.vdpVideo.pause()
        elif self.vdpVideo.isPaused(): 
            print "Change to play"
            self.vdpVideo.play()
        else:
            # There is no media being played/paused. The state is 'stop'.
            # Select one video and play it.
            if self.lswPlaylist.currentRow() < 0:
                # Nothing has been played.
                # Select the first item
                self.lswPlaylist.setCurrentRow(0, QtGui.QItemSelectionModel.SelectCurrent)
            
            # Now play the video.
            self.on_lswPlaylist_doubleClicked()
    # Response to timer event.
    @QtCore.pyqtSlot()
    def on_tmrTimer_timeout(self):
        # Update the playing time and the label.
        currentTime = self.vdpVideo.currentTime()

        if currentTime == 0:
            # This is the first time the label is changed.
            self.lblTime.setText('')
        else:
            # Get the total play time
            totalTime = self.vdpVideo.totalTime()
            # If the total playing time is less than 1 hour, just show minutes
            # and seconds.
            tFormat = 'mm:ss' if totalTime < 3600000 else 'hh:mm:ss'

            # We use Qtime for time conversions.
            currentTimeH = QtCore.QTime()

            # Convert times to a human readable strings.
            ct = currentTimeH.addMSecs(currentTime).toString(tFormat)

            totalTimeH = QtCore.QTime()
            tt = totalTimeH.addMSecs(totalTime).toString(tFormat)

            # Set time to label.
            self.lblTime.setText(ct + '/' + tt)

        # Now update the mouse status.
        # The window is in full-screen mode...
        if self.isFullScreen():
            # Update the current mouse time and position.
            mousePos = QtGui.QCursor.pos()
            mouseT = QtCore.QTime.currentTime()

            # Normally, when the program is in full-screen mode, the mouse must
            # be hidden until user move it.
            if (mousePos != self.mousePos0 and self.cursor().shape() == QtCore.Qt.BlankCursor) or self.wdgVideoControls.isVisible():
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

                # Reset the time count for calculating the mouse moving time.
                self.mouseT0 = QtCore.QTime.currentTime()
            # If user stops moving the mouse, it must stay visible at least some
            # seconds.
            elif self.cursor().shape() == QtCore.Qt.ArrowCursor and self.mouseT0.secsTo(mouseT) > 1:
                self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

            # Update the current mouse position.
            self.mousePos0 = mousePos

            # Convert the global mouse position in the screen to the window
            # local coordinates. And get the coordinate for Y axis.
            mouseY = self.mapFromGlobal(mousePos).y()

            # If the mouse approaches to the position in which must be the
            # controls bar, it must be visible.
            if mouseY < self.height() and \
                mouseY > self.height() - self.wdgVideoControls.height():
                if self.wdgVideoControls.isHidden():
                    self.wdgVideoControls.show()
            # otherwise it must stay hidden.
            elif self.wdgVideoControls.isVisible():
                self.wdgVideoControls.hide()
        # The window is in normal mode...
        else:
            # If the mouse cursor is hidden, show it.
            if self.cursor().shape() == QtCore.Qt.BlankCursor:
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

            # Show play list.
            if self.wdgVideoControls.isHidden():
                self.wdgVideoControls.show()


    # mouseDoubleClickEvent is a protected method which called when user
    # double clicks in the GUI and this event isn't caught by any other widget.
    def mouseDoubleClickEvent(self, event):
        # Always, before process the event, we must send a copy of it to the
        # ancestor class.
        QtGui.QMainWindow.mouseDoubleClickEvent(self, event)

        # Go to full-screen mode or exit from it.
        self.on_btnFullscreen_clicked()
        
    
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
            
    # Get direct link for one video.
    def getYoutubeLinkToPlay(self, link):
        try:
            # In this version, we will just get any link.
            print "Decoding the link", str(link)            
            # Get the video quality.
            desired_resolution = str(self.cbQuality.currentText())
            print "Desired resolution:", desired_resolution
            
            # Find the resolution nearest to the desired resolution.
            direct_link = YouTubeDl().getDirectLink(link, desired_resolution)
            self.emit(QtCore.SIGNAL("doneGetDirectLinks(QString)"), QtCore.QString(direct_link))
        except:
            self.emit(QtCore.SIGNAL("IWantToBeNoticed(QString)"), QtCore.QString("Sorry, it seems that you have to watch this video on YouTube."))
            
    def playVideo(self, link):
        print "link:", link
        match = re.search(r'(.*)\n\"(.*)\"', link)
        if match:
            link = match.group(1)
            
        # Play the video.
        if link.startsWith(QtCore.QString(r'http://')) or link.startsWith(QtCore.QString(r'https://')) or link.startsWith(QtCore.QString(r'mms://')):
            print "Link: via web"
            print "Asking the phonon player to play."
            self.vdpVideo.play(phonon.Phonon.MediaSource(QtCore.QUrl(link)))
            self.currentDirectLink = str(link);
        else:
            print "Link: local file"
            self.vdpVideo.play(phonon.Phonon.MediaSource(link))
            print "Asking the player to play."
            
    
    @QtCore.pyqtSlot()
    def on_btnDownloadPlaying_clicked(self):
        try:
            # In this version, we will just get any link.
            link = self.entry.media.player.url            
            # Get the video quality.
            desired_resolution = str(self.cbQuality.currentText())
            
            # Find the resolution nearest to the desired resolution.
            direct_link = YouTubeDl().getDirectLink(link, desired_resolution)
            match = re.search(r'(.*)\n\"(.*)\"', direct_link)
            if match:
                media = [match.group(1), match.group(2)]
            command = 'aria2c "%s" -o %s' %(media[0], media[1])
            command =  command.replace("\n", "")
            print command.find("\n")
            Popen(command, shell=True, close_fds=True)
        except:
            self.emit(QtCore.SIGNAL("IWantToBeNoticed(QString)"), QtCore.QString("Sorry, it seems that you have to watch this video on YouTube."))      
        
        
            
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
            self.entry = entry
            # Start a thread getting the direct link play.
            self.lswPlaylist.setCurrentRow(0)
            self.startThread(self.getYoutubeLinkToPlay, QtCore.SIGNAL("doneGetDirectLinks(QString)"), QtCore.SIGNAL("failedGetDirectLinks(QString)"), self.playVideo, self.dummy, self.entry.media.player.url)
        
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
        # upload the file.
        
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
        print "trying..."
        
        # Show an upload dialog.
        uploadDialog = UploadStatusDialog('Uploading', video_title, video_location, self)
        uploadDialog.show()
        self.startThread(self.doRealUpload,
                         QtCore.SIGNAL("doneUpload(QString)"),
                         QtCore.SIGNAL('uploadFailed(QString)'),
                         self.doneUpload,
                         self.uploadFailed, video_title, description, tags, video_location, uploadDialog)
    
    # Do the upload.
    def doRealUpload(self, video_title, description, tags, video_location, uploadDialog):
        print  "doRealUPload"     
        try:
            self.getYouTubeService()
            new_entry = self.yt_service.DirectVideoUpload(video_title, description, tags, video_location)
            self.emit(QtCore.SIGNAL('doneUpload(QString)'), QtCore.QString(video_location))
            # Setting the upload dialog.
            uploadDialog.lbStatus.setText(QtCore.QString('Video uploaded. Waiting for YouTube\'s acceptance.'))
            
            # Wait and check for Youtube Status.
            for i in range(10):  # wait for at most 10 * 30 seconds.
                time.sleep(30)
                uploadStatus = self.yt_service.client.CheckUploadStatus(new_entry)
                if uploadStatus is not None:
                    status = str(uploadStatus[0])
                    print status
                    uploadDialog.lbStatus.setText(QtCore.QString(status))
                else:
                    uploadDialog.lbStatus.setText(QtCore.QString("Done."))
                    break
        except:
            self.emit(QtCore.SIGNAL('uploadFailed(QString)'), QtCore.QString(video_location))
            uploadDialog.lbStatus.setText(QtCore.QString('Failed.'))
        
    # A message notifying upload sucessfully event.
    def doneUpload(self, message):
        pass
        # self.uploadingList[str(message)].lbStatus.setText(QtCore.QString('Done.'))
        
    def uploadFailed(self, message):
        pass
        # self.uploadingList[str(message)].lbStatus.setText(QtCore.QString('Failed.'))
        
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
            feed = yt_service.RetrieveMostRespondedVideoFeed()
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
        '''
        Log in to YouTube, using an email and password. 
        '''
        print "Inside the login function"
        print email, type(email)
        try:
            self.yt_service = YouTubeService(email, password)
            self.logged_in = self.yt_service.loggedIn
            if (self.logged_in):
                self.emit(QtCore.SIGNAL("doneLogin(QString)"), email)
            else:
                self.emit(QtCore.SIGNAL("failedLogin()"))
        except:
            self.emit(QtCore.SIGNAL("failedLogin()"))
            
    
    @QtCore.pyqtSlot()
    def on_btnPost_clicked(self):
        '''
        Post a comment to the current video.
        If the user has logged in, post a comment, otherwise display a warning message.
        '''
        if self.yt_service == None or self.yt_service.loggedIn == False:
            messageBox = WarningDialog.WarningDialog("Sorry, you have to log in first.", self)
            messageBox.show()            
        else:
            # Get the in the textEditComment
            text = str(self.textEditComment.toPlainText())
            print "You want to post a comment:", text
            self.startThread(self.postComment, QtCore.SIGNAL("donePostComment()"), QtCore.SIGNAL("failedPostComment()"), self.dummy, self.dummy, text)
            
    def postComment(self, comment):
        '''
        Post a comment to the playing video.
        '''
        print "You want to post a comment."
        try:
            self.yt_service.AddComment(getVideoId(self.entry), comment)
            self.emit(QtCore.SIGNAL("donePostComment()"))
        except:
            self.emit("failedPostComment()")
    
    @QtCore.pyqtSlot()
    def on_btnRate_clicked(self):
        '''
        Handle the event that the user click on the 'Rate' button.
        '''
        print "You want to rate the video."
        if self.logged_in:
            self.startThread(self.addRating, QtCore.SIGNAL("doneAddRating()"), QtCore.SIGNAL("failedAddRating()"), self.dummy, self.dummy)
        else:
            message = WarningDialog.WarningDialog("Sorry, you have to log in first.", self)
            message.showNormal()
            
    def addRating(self):
        '''
        Rate the current (playing) video.
        '''
        number = self.value()
        try:
            self.yt_service.AddRating(getVideoId(self.entry), number)
            self.emit(QtCore.SIGNAL("doneAddRating()"))
        except:
            self.emit(QtCore.SIGNAL("failedAddRating()"))
        
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
    
    @QtCore.pyqtSlot()
    def on_btnLogout_clicked(self):
        self.yt_service = YouTubeService()
        self.logged_in = False
        self.labelGreeting.setText('Hello')
        
    # Show the username.
    def setUsernameView(self, username):
        self.labelGreeting.setText("Hello, %s" % username)
        self.ledUsername.setText('')
        self.ledPassword.setText('')
        self.btnLogout.setEnabled(True)
        
    def failedLoginWarning(self):
        print "Sorry, login failed!"
        self.yt_service = YouTubeService()
        self.btnLogout.setEnabled(False) 
        warningDialog = WarningDialog.WarningDialog(warning="Sorry, logging in failed", parent=self)
        warningDialog.show()
    
    def _htmlForFlash(self, url):
        html = ''''<embed src="%s" type="application/x-shockwave-flash" allowfullscreen="true" width="640" height="480"></embed>
        ''' % url
        
        return html
    
    def showMessage(self, message):
        wd = WarningDialog.WarningDialog(message, self)
        wd.show() 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Simple player')

    # Create a UI instance.
    videoPlayer = VideoPlayer()

    # Show the UI.
    videoPlayer.show()
    app.exec_()

