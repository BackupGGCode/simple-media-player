import urllib,re

from bs4 import BeautifulSoup

def parseYouTubePage(url):
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)
    head_tag = soup.find('div', id="yt-masthead-container")
    if (head_tag):
        head_tag.extract()
    alert_tag = soup.find('div', id = 'alerts')
    if alert_tag:
        alert_tag.extract()
    footer_tag = soup.find('div', id = 'footer-hh-container')
    if footer_tag:
        footer_tag.extract()
    for sidebar in soup.findAll('div', re.compile('.*sidebar.*')):
        sidebar.extract()
    
    for redirect in soup.findAll('area', re.compile('.*redirect.*')):
        redirect.extract()
        
    for div in soup.findAll('div', "comments-post-container clearfix"):
        div.extract()
    
        
    return unicode(soup)