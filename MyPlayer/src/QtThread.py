from PyQt4 import QtCore

# A generic thread class.
# To create a thread running a function f:
# GenericThread(<function name>, <function arguments>)

class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    
    def run(self):
        self.function(*self.args,**self.kwargs)
