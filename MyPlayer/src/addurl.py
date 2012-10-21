

from PyQt4 import QtCore, QtGui, uic
import sys

class AddURL(QtGui.QDialog):
    def __init__(self, parent = None):
        super(AddURL, self).__init__(parent  = parent)
        
        # Load the UI file.
        uic.loadUi('../share/ui/addurl.ui', self)
    
    @QtCore.pyqtSlot()
    def on_bbxAcceptCancel_accepted(self):
        # Read the text from QPlainTextEdit.
        # Each line is an URL.
        # Note: No URL checking has been implemented.
        self.urls = str(self.txtURLList.toPlainText()).split()
 
        # Sort the URL list.
        self.urls.sort()
 
        # Close the dialog and return 0, this means that the user accepted the
        # action.
        self.done(0)
 
    @QtCore.pyqtSlot()
    def on_bbxAcceptCancel_rejected(self):
        # Close the dialog and return 1, this means that the user cancelled the
        # action.
        self.done(1)
 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    au = AddURL()
    au.show()
    return_code = app.exec_()
    sys.exit(return_code)
    
            