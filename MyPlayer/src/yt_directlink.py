#!/usr/bin/env python

import re
import urllib

# Clean up path link.
def escape_file_path(path):
    path = path.replace('/', '-')
    path = path.replace('\\', '-')
    path = path.replace('*', '-')
    path = path.replace('?', '-')
    return path

# Convert html encoding to unicode.
# TODO: convert to unicode: range > 256 
def unicodize(text):
    return re.sub(r'\\u([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])', lambda x: chr(int(x.group(0)[2:], 16) % 256), text)

# Decode a URL.
def decode_url(string):
    decoder = [',', '%2C',' ', '%20', '<', '%3C', '>', '%3E', '#', '%23', '%', '%25', '{', '%7B', '}', '%7D', '|', '%7C', '\\', '%5C', '^', '%5E', '~', '%7E', '[', '%5B', ']', '%5D', '`', '%60', ';', '%3B', '/', '%2F', '?', '%3F', ':', '%3A', '@', '%40', '=', '%3D', '&', '%26', '$', '%24']
    for i in range(0, len(decoder) - 1, 2):
        string = string.replace(decoder[i + 1], decoder[i])
    
    return string


# Decode  a html string.
def decode_html(string): 
    url = unicodize(string)
    url = re.sub(r'\\/', '/', url)
    url = decode_url(url)
    url = url.replace('url=http://', '\nhttp://')
    url = url.replace('url=https://', '\nhttps://')    
    strings = []    
    for string in url.split('\n'):
        if string.find('-o--') != -1:
                strings.append(string.replace(r'&amp', r'&'))
    
    for link in strings:
        # Get the type, quality, signature.
        # link = string + &type=[...]&sig=[...]&quality=[...]
        split1 = link.split("&type=")
        split2 = split1[1].split("&sig=")
        split3 = split2[1].split("&quality=")
        
        
        t = split2[0].split(';')[0] # The word 'type' is used by python.
        direct_link = split1[0] + "&signature=" + split3[0]
        quality = split3[1].split(',')[0]
        
        print "#################################################################"
        print direct_link
        print quality
        print t
        
if __name__ == '__main__':
    socket = urllib.urlopen("https://www.youtube.com/watch?v=J6ZWlDks0nQ")
    page = socket.read()
    socket.close()
    
    doc = decode_html(page)
    
    
    
    
    
    
    
    
    
    


#def youtube_download_by_id(id, title = None, output_dir = '.', merge = True, info_only = False):
#    html = request.urlopen('http://www.youtube.com/watch?v=' + id).read().decode('utf-8')
#    
#    title = r1(r'"title": "([^"]+)"', html)
#    title = unicodize(title)
#    title = parse.unquote(title)
#    title = escape_file_path(title)
#    
#    url = r1(r'crossdomain.xml"\);yt.preload.start\("([^"]+)"\)', html)
#    url = unicodize(url)
#    url = re.sub(r'\\/', '/', url)
#    url = re.sub(r'generate_204', 'videoplayback', url)
#    
#    type, ext, size = url_info(url)
#    
#    print_info(site_info, title, type, size)
#    if not info_only:
#        download_urls([url], title, ext, size, output_dir, merge = merge)
#
#def youtube_download(url, output_dir = '.', merge = True, info_only = False):
#    id = parse.parse_qs(parse.urlparse(url).query)['v'][0]
#    assert id
#    
#    youtube_download_by_id(id, None, output_dir, merge = merge, info_only = info_only)
#
#site_info = "YouTube.com"
#download = youtube_download
#download_playlist = playlist_not_supported('youtube')
