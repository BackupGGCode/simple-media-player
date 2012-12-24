# Wrapper for the file youtube-dl.py
import subprocess
import re
class YouTubeDl:
    def __init__(self):
        #print "Nothing to do."
        pass
    def getDirectLink(self, url, preferred_quality):
        output = None
        try:
            command = r'youtube-dl.exe --restrict-filenames --get-filename -o "%(title)s.%(ext)s" -g --max-quality ' + preferred_quality + " " + url    
            output = subprocess.check_output(command.split())
        except:
            output = None
        if output == None:
            try:
                command = r'youtube-dl.exe --restrict-filenames --get-filename -o "%(title)s.%(ext)s" -g ' + url
                output = subprocess.check_output(command.split())
            except:
                output = None
        return output
if __name__ == "__main__":
    yd = YouTubeDl()
    links = yd.getDirectLink("http://www.youtube.com/watch?v=nj4MDjx5vRE", "1080p")
    #for link in links:
    #    print links