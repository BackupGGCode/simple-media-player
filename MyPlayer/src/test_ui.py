from PyQt4 import QtGui, uic
import sys

class TestUI(QtGui.QMainWindow):
    def __init__(self):
        super(TestUI, self).__init__()
        uic.loadUi('../share/ui/new_ui.ui', self)
        self.show()
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    testui = TestUI()
    sys.exit(app.exec_())
    
        