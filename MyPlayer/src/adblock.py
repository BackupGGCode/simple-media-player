# https://www.youtube.com/watch?v=OHkvan-NFnM&feature=youtube_gdata_player

import sys
from PyQt4 import QtCore, QtGui, QtNetwork
from PyQt4.QtNetwork import QNetworkAccessManager
from PyQt4.QtWebKit import QWebView

class NetWorkManager(QNetworkAccessManager):
    def __init__(self):
        super(NetWorkManager, self).__init__()
    
    def createRequest(self, op, request, device = None ):
        path = str(request.url().path())
        lower_case = path.lower()
        lst = ["banner", "ads", r"||youtube-nocookie.com/gen_204?", r"youtube.com###watch-branded-actions", "imagemapurl"]
        block = False
        for l in lst:
            if lower_case.find(l) != -1:
                block = True
                break
        if block:
            print "Skipping"
            print request.url().path()
            return QNetworkAccessManager.createRequest(self, QNetworkAccessManager.GetOperation, QtNetwork.QNetworkRequest(QtCore.QUrl()))
        else:
            return QNetworkAccessManager.createRequest(self, op, request, device)


# Usage example.    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    wv = QWebView()
    nam = NetWorkManager()
    wv.page().setNetworkAccessManager(nam)
    wv.load(QtCore.QUrl(r'https://www.youtube.com/watch?v=OHkvan-NFnM&feature=youtube_gdata_player'))
    wv.show()

    app.exec_()
            
    

