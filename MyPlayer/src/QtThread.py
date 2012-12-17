# -*- coding: utf-8 *-*
import threading

# A generic thread class.
# To create a thread running a function f:
# GenericThread(<function name>, <function arguments>)

#class GenericThread(QtCore.QThread):
#    def __init__(self, function, *args, **kwargs):
#        QtCore.QThread.__init__(self)
#        self.function = function
#        self.args = args
#        self.kwargs = kwargs
#
#    def __del__(self):
#        self.wait()
#
#    
#    def run(self):
#        self.function(*self.args,**self.kwargs)

#This type of thread is stoppable!
class GenericThread(threading.Thread):
    def __init__(self, function, *args, **kwargs):
        super(GenericThread, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()

    
    def run(self):
        self.function(*self.args,**self.kwargs)

