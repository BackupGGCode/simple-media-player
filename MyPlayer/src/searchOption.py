from PyQt4 import QtGui, uic


class SearchOptionDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(SearchOptionDialog, self).__init__(parent = None)
        uic.loadUi('../share/ui/advanced_search.ui', self)
        