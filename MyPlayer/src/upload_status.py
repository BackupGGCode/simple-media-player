import math, sys
from PyQt4 import uic
from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import *

class UploadStatusDialog(QDialog):
    def __init__(self, status='Uploading ...', video_title='', video_location='', parent=None):
        super(UploadStatusDialog, self).__init__(parent=parent)
        uic.loadUi('../share/ui/upload_status.ui', self)
        self.lbStatus.setText(status)
        self.lbTitle.setText(video_title)
        self.lbLocation.setText(video_location)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    us = UploadStatusDialog('Uploading ...', 'A sample video', 'C:/video/sample.avi')
    us.show()
    app.exec_()    
        
