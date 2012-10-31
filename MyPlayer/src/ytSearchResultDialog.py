from PyQt4 import QtGui, uic

class YoutubeSearchResultDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(YoutubeSearchResultDialog, self).__init__(parent = parent)
        
        # Load the UI
        uic.loadUi("../share/ui/listVideo.ui", self)
        self.setModal(False)
            