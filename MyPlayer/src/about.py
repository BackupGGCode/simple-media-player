from PyQt4 import QtGui, uic
import sys

class About(QtGui.QDialog):
    def __init__(self, parent = None):
        super(About, self).__init__(parent = parent)
        
        # Load the UI
        uic.loadUi("../share/ui/about.ui", self)
        

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ab = About()
    ab.show()
    app.exec_()
    