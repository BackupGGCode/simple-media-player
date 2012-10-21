# -*- coding: utf-8 *-*
###############################################################################
# A simple media player.
# This project is based on the tutorial
#
#
#

# A simple player
import sys
import os
import random
from PyQt4 import QtCore, QtGui, uic, phonon

import addurl
import about

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
        uic.loadUi('../share/ui/videoplayer_mod.ui', self)

        #######################################################################
        # Initialize the play list.
        #######################################################################
        self.playlist = []
        self.playlistTmp = []
        self.repeat = False

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
        self.on_lswPlaylist_doubleClicked(self.lswPlaylist.item(index))
        
            
                
        

    # Event: The 'play/pause' is pressed.
    @QtCore.pyqtSlot()
    def on_btnPlayPause_clicked(self):
        # If there is some selected item, and it is either 'playing' or 
        # 'paused', then switch between the two states.
        if self.vdpVideo.mediaObject().state() == phonon.Phonon.PlayingState:
            self.vdpVideo.pause()
        elif self.vdpVideo.mediaObject().state() == phonon.Phonon.PausedState:
            self.vdpVideo.play()
            
        # If there aren't a selected media in the play list, then select the 
        # first one in the list and play it.
        elif self.lswPlaylist.currentRow() < 0:
            # Select the first item.
            self.lswPlaylist.setCurrentRow(0, QtGui.QItemSelectionModel.\
                                                    SelectCurrent)
            # Call this to play it.
            self.on_lswPlaylist_doubleClicked(self.lswPlaylist.currentItem())
        else:
            # Play the current item. In this case, it is not selected, but the 
            # state is 'stopped'
            self.on_lswPlaylist_doubleClicked(self.lswPlaylist.currentItem())

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
        if self.vdpVideo.videoWidget().aspectRatio() == \
            phonon.Phonon.VideoWidget.AspectRatioWidget:
            self.vdpVideo.videoWidget().\
                            setAspectRatio(phonon.Phonon.VideoWidget.\
                                                        AspectRatioAuto)
        else:
            self.vdpVideo.videoWidget().\
                            setAspectRatio(phonon.Phonon.VideoWidget.\
                                                        AspectRatioWidget)

    # Action: Click on the 'Show Play list' button.
    @QtCore.pyqtSlot()
    def on_btnShowPlayList_clicked(self):
        pass

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
    def on_lswPlaylist_doubleClicked(self, model_index):
        # If the play list is empty, do nothing.
        if self.playlist == []:
            return
        # Get the index of model_index, use it to obtain corresponding MediaSource
        # Here model_index is of the type QtGui.QListWidgetItem.
        try:
            # Get the index of model_view, use it to obtain the corresponding
            # MediaSource, and then play it.
            # Here model_index is of the type QtGui.QListWidgetItem.
            self.vdpVideo.play(self.playlist[model_index.row()])
        except:
            # Here model_index is of the type QtGui.QModelIndex.
            self.vdpVideo.play(self.playlist[self.lswPlaylist.row(model_index)])
    
    # Add local file
    @QtCore.pyqtSlot()
    def on_axnAddLocalFile_triggered(self):
        # Open the "File selection" dialog
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
            # Add the URLs to the play list.
            self.addMedias(addURLDlg.urls)


    # Add to the play list a list of local files.
    def addMedias(self, medias=[]):
        # Sort the list by name.
        medias.sort()

        play = False

        if medias != []:
            # If the play list if currently empty, add files listed in medias
            # to the list and set play to 'True'
            if self.playlist == []:
                play = True

            # Add files to the play list.
            # Two cases: Local file / online file
            for media in medias:
                try:
                    if isinstance(media, str):
                        if media.startswith('http://') or media.startswith('https://') or media.startswith('mms://'):
                            self.playlist += [phonon.Phonon.MediaSource(QtCore.QUrl(media))]
                    else:
                        self.playlist += [phonon.Phonon.MediaSource(media)]
                        print "Adding off-line video"
                except:
                    """
                    This version: ignore error here.
                    """
                    print "An error has occurred" 
                                    
            # update the play list.
            self.updatePlayList()

        # If the play list has been loaded and there aren't a media playing,
        # play it.
        if play and self.vdpVideo.mediaObject().state() != phonon.Phonon.PlayingState:
            self.on_btnPlayPause_clicked()

    # Update the play list.
    def updatePlayList(self):
        # Create an empty play list.
        playlist = []

        # For each media to play.
        for source in self.playlist:
            # If the media is a local file...
            if source.type() == phonon.Phonon.MediaSource.LocalFile:
                # Just add the name of the file without the path.
                playlist += [os.path.basename(str(source.fileName()))]
            # If the media is an URL...
            elif source.type() == phonon.Phonon.MediaSource.Url:
                print "Updating the play list: Online version."
                # Add the URL to the list.
                playlist += [str(source.url().toString())]

        # Remove all items in QListWidget
        self.lswPlaylist.clear()

        # add the new play list.
        self.lswPlaylist.addItems(playlist)
        
    
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

