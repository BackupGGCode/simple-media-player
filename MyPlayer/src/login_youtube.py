import sys
from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebView
from PyQt4.QtWebKit import QWebSettings, QWebPage

class Browser(QWebPage):
    def __init__(self):
        super(QWebPage, self).__init__()

    def userAgentForUrl(self, url):
        return "Mozilla/5.0 (X11; Linux x86_64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"


def fillForm(web, username, password):
    print "Filling in the form"
    doc = web.page().mainFrame().documentElement()
    
    print "Finding username tag"
    user = doc.findFirst("input[id=Email]")
    print "Finding passwd tag"
    passwd = doc.findFirst("input[id=Passwd]")    
    
    print "Setting information"
    user.evaluateJavaScript("this.value = '%s'" % username)
    passwd.evaluateJavaScript("this.value = '%s'" % password)    
    button = doc.findFirst("input[id=signIn]")
    button.evaluateJavaScript("this.click()")
          
def doLogin(web, url, username, password):        
    web.loadFinished.connect(lambda: fillForm(web, username, password))
    web.load(url)
    web.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    web = QWebView()
    settings = web.settings()
    settings.setAttribute(QWebSettings.PluginsEnabled, True)
    web.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
    web.setPage(Browser())
    
    url = QUrl(r"https://accounts.google.com/Login")
    username = raw_input("Username: ")
    password = raw_input("Password: ")
    doLogin(web, url, username, password)
    app.exec_()
