import sys
from PyQt4 import QtCore, QtGui, uic

class UploadDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(UploadDialog, self).__init__(parent = parent)
        uic.loadUi('../share/ui/upload.ui', self)
        self.fileDialog = QtGui.QFileDialog()
        
    @QtCore.pyqtSlot()
    def on_btnChooseUploadFile_clicked(self):
        filename = self.fileDialog.getOpenFileName()
        self.lineEditFilePath.setText(filename)
        print filename
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ul = UploadDialog()
    ul.show()
    sys.exit(app.exec_())