from PyQt4 import QtGui, uic

class WarningDialog(QtGui.QDialog):
    def __init__(self, warning = "",parent = None):
        QtGui.QDialog.__init__(self, parent = parent)        
        uic.loadUi('../share/ui/login_failed.ui', self)
        message = '<html><head/><body><p align="center"><span style=" font-size:14pt; color:#000000;">%s</span></p></body></html>' % warning
        self.label.setText(message)
        