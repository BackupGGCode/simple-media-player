# -*- coding: utf-8 *-*
###############################################################################
# A simple media player.
# This project is based on the tutorial
#
#
#

# A simple player
import sys
import random
from PyQt4 import QtCore, QtGui, uic, phonon
from PyQt4.QtWebKit import QWebPage

from ytSearchResultDialog import YoutubeSearchResultDialog

import gdata.youtube.service

# Two additional UI module.
import addurl
import about
import print_entry


class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    
    def run(self):
        self.function(*self.args,**self.kwargs)
        return
    
    

###############################################################################
# A class represent a simple media player.
###############################################################################
class VideoPlayer(QtGui.QMainWindow):

    def __init__(self):
        #######################################################################
        # Initialize: calling the inherited __init__ function.
        #######################################################################
        super(VideoPlayer, self).__init__()


        #######################################################################
        # Load the defined UI.
        #######################################################################
        uic.loadUi('../share/ui/videoplayer.ui', self)

        #######################################################################
        # Initialize the play list.
        # Set some initial playing option.
        #######################################################################
        self.playlist = [] # A list of links to the file to play.
        self.playlistTmp = [] # A temporary play list, use to shuffle play list.
        self.repeat = False # Default mode: not repeating the play list.

        #######################################################################
        # Connect the player with the volume and the time sliders.
        #######################################################################
        self.sldVolumeSlider.setAudioOutput(self.vdpVideo.audioOutput())
        self.sldSeekSlider.setMediaObject(self.vdpVideo.mediaObject())

        #######################################################################
        # Creating a menu for adding media.
        #######################################################################
        self.addMediaMenu = QtGui.QMenu()
        # Add local file option
        self.axnAddLocalFile = self.addMediaMenu.addAction(self.tr('Add local &File'))
        # Add link option
        self.axnAddURL = self.addMediaMenu.addAction(self.tr('Add &URL'))
        # Actually attach the menu to the button.
        self.btnAddMedia.setMenu(self.addMediaMenu)
        #Connect these to actions.
        self.axnAddLocalFile.triggered.connect(self.on_axnAddLocalFile_triggered)
        self.axnAddURL.triggered.connect(self.on_axnAddURL_triggered)

        #######################################################################
        # Create a timer. This will be used to show the playing time.
        #######################################################################
        self.tmrTimer = QtCore.QTimer(self)
        # This will emit a signal every 1/4 second.
        self.tmrTimer.setInterval(250)
        # Connect the signal emitted to the action self.on_tmrTimer_timeout
        self.tmrTimer.timeout.connect(self.on_tmrTimer_timeout)
        # start the timer.
        self.tmrTimer.start()

        #######################################################################
        # initialize the current mouse position and time.
        #######################################################################
        self.mousePos0 = QtGui.QCursor.pos()
        self.mouseT0 = QtCore.QTime.currentTime()

        
        #######################################################################
        # The search tab.
        #######################################################################
        # Search box: Enter pressed.
        self.lineEditSearch.returnPressed.connect(self.on_btnSearchVideo_clicked)
        
        #######################################################################
        # The dock widget: show or hide?
        #######################################################################
        self.dckShown = True
        
        self.lineEditSearch.setFocus()        
        
        
        #######################################################################
        # The dialog showing search result.
        #######################################################################
        self.initSearchResultDialog()
        self.searchResultDialog.videoList.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.searchResultDialog.videoList.linkClicked.connect(self.linkClicked)
        
        
        #######################################################################
        # Search thread.
        #######################################################################
        self.threadPool = []
        
    def linkClicked(self, url):
        print url.toString()
    
    
    # Initialize the search result dialog.
    def initSearchResultDialog(self):
        self.searchResultDialog = YoutubeSearchResultDialog()
        self.searchResultDialog.hide()
        self.searchResultDialog.btnListOK.clicked.connect(self.processSearchResultDialogCommand)
    
    def processSearchResultDialogCommand(self):
        print self.searchResultDialog.lineEdit.text()
    
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
        print safe
        
        # searching not done: Print the defaul message.
        self.searchResultDialog.videoList.setHtml("<html><body><h1>Searching ...</h1></body></html>")
        
        # Create a thread to do the search.
        self.threadPool.append(GenericThread(self.ytSearch, order, safe, self.lineEditSearch.text()))        
        self.disconnect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.connect(self, QtCore.SIGNAL("doneSearching(QString)"), self.setHtml)
        self.threadPool[len(self.threadPool) - 1].start()
        
        self.searchResultDialog.show()
        self.setFocus()
    
    def setHtml(self, html):
        print html
        print "Setting the html content"
        self.searchResultDialog.videoList.setHtml(html)
        
    def ytSearch(self, order, safe, vq):
        print "Searching option:"
        print "Query:", vq
        print "Order:", order
        print "Safe search:", safe
        
        html = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title>Search Result</title></head><body><ol>'
        
        try:
            # Init service.
            yt_service = gdata.youtube.service.YouTubeService()
            
            # Init search query.
            query = gdata.youtube.service.YouTubeVideoQuery()    
            query.orderby = order
            query.safeSearch = safe
            query.vq = str(vq)
            
            # Run the query.
            print "Running the query"
            feed = yt_service.YouTubeQuery(query)
            print "Query: Done"
            
            for entry in feed.entry:
                html += "<li>%s</li>" % print_entry.getHtmlEntry(entry)
            
        except:
            print "Some thing wicked happened!"
        html += "</ol></body></html>"
        
        self.emit(QtCore.SIGNAL('doneSearching(QString)'), html)
        
    def closeEvent(self, event):
        # Close the search result dialog also.
        if self.searchResultDialog:
            self.searchResultDialog.close()
        self.destroy()
            
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
        self.on_lswPlaylist_doubleClicked(self.lswPlaylist.item(index))

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


    # ACtion: click on the 'Repeat' button.
    @QtCore.pyqtSlot()
    def on_btnRepeatPlayList_clicked(self):
        self.repeat = not self.repeat

    # Action: click on the 'Video Fill' button.
    @QtCore.pyqtSlot()
    def on_btnVideoFill_clicked(self):
        # If the btnVideoFill button is checked, the video will be stretched to
        # fill the entire video widget.
        # otherwise, the video will be preserve it's aspect ratio.
        if self.vdpVideo.videoWidget().aspectRatio() == phonon.Phonon.VideoWidget.AspectRatioWidget:
            self.vdpVideo.videoWidget().setAspectRatio(phonon.Phonon.VideoWidget.AspectRatioAuto)
        else:
            self.vdpVideo.videoWidget().setAspectRatio(phonon.Phonon.VideoWidget.AspectRatioWidget)

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
        # Play the video.
        if link.startsWith(QtCore.QString(r'http://')) or \
            link.startsWith(QtCore.QString(r'https://')) or \
            link.startsWith(QtCore.QString(r'mms://')):
            self.vdpVideo.play(phonon.Phonon.MediaSource(QtCore.QUrl(link)))
        else:
            self.vdpVideo.play(phonon.Phonon.MediaSource(link))
        

    # Add local file
    @QtCore.pyqtSlot()
    def on_axnAddLocalFile_triggered(self):
        # Open the "File selection" dialog. Each items of filenames is a 'QString'
        filenames = QtGui.QFileDialog.getOpenFileNames(self, self.tr('Add local files'))
        
        # Add the file names to the play list.
        self.addMedias(filenames)
        

    # Add URL
    @QtCore.pyqtSlot()
    def on_axnAddURL_triggered(self):
        # Create an instance for the "Add URL" dialog.
        addURLDlg = addurl.AddURL(self)

        # Open the dialog.
        # The program execution will stop here until user close the dialog.
        addURLDlg.exec_()
        
        if addURLDlg.result() == 0:
            #Convert the file names to QString.
            lst = []
            for filename in addURLDlg.urls:
                lst.append(QtCore.QString(filename))
            # Add the URLs to the play list.
            print lst
            self.addMedias(lst)

    # Add to the play list a list of local files.
    def addMedias(self, medias=[]):
        # Sort the list by name.
        medias.sort()
        play = False

        if medias != []:
            # If the play list if currently empty, add files listed in medias
            # to the list and set play to 'True'
            if self.playlist == []:
                print "play = True"
                play = True
            
            self.playlist += medias

            # update the play list.
            self.updatePlayList()

        # If the play list has been loaded and there aren't a media playing,
        # play it.
        if play and self.vdpVideo.mediaObject().state() != phonon.Phonon.PlayingState:
            print "Now play the newly added media"
            self.on_btnPlayPause_clicked()

    # Update the play list.
    def updatePlayList(self):
        # Remove all items in QListWidget
        self.lswPlaylist.clear()

        # add the new play list.
        self.lswPlaylist.addItems(self.playlist)


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
            if (mousePos != self.mousePos0 and \
                self.cursor().shape() == QtCore.Qt.BlankCursor) or \
                self.wdgVideoControls.isVisible():
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

                # Reset the time count for calculating the mouse moving time.
                self.mouseT0 = QtCore.QTime.currentTime()
            # If user stops moving the mouse, it must stay visible at least some
            # seconds.
            elif self.cursor().shape() == QtCore.Qt.ArrowCursor and \
                    self.mouseT0.secsTo(mouseT) > 1:
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

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Simple player')

    # Create a UI instance.
    videoPlayer = VideoPlayer()

    # Show the UI.
    videoPlayer.show()
    app.exec_()

