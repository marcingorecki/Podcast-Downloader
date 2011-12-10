import urllib2
import re
import os.path
import argparse
from datetime import datetime
from xml.dom.minidom import parse, parseString

podcast_path = "podcasts/"

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc).encode('ascii', 'ignore')

def downloadFileWithPassword(url, username, password):
    # create a password manager
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, url, username, password)
    
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    
    # create "opener" (OpenerDirector instance)
    opener = urllib2.build_opener(handler)
    
    # use the opener to fetch a URL
    opener.open(url)
    
    # Install the opener.
    # Now all calls to urllib2.urlopen use our opener.
    urllib2.install_opener(opener)
    #downloadFile(url, file_name)
    response = urllib2.urlopen(url)
    the_page = response.read()
    return the_page

def downloadFile(url, file_name):
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)
    
    file_size_dl = 0
    block_sz = 8192
    while True:
        rBuffer = u.read(block_sz)
        if not rBuffer:
            break
    
        file_size_dl += len(rBuffer)
        f.write(rBuffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print "\b\b\b\b\b\b\b\b\b\b\b" + status,
    
    f.close()
    
def downloadPodcasts(podcast_xml):
    dom = parseString(podcast_xml)
    podcasts = dom.getElementsByTagName("item")
    
    for podcast in podcasts:
            title = podcast.getElementsByTagName("title")[0]
            url = podcast.getElementsByTagName("enclosure")[0].getAttribute("url")
            
            podcast_name = getText(title.childNodes)
            m = re.search('(.*). (\d+ \w+ \d+)', podcast_name)
            
            date = datetime.strptime(m.group(2), "%d %b %y")
            new_date = datetime.strftime(date,"%Y-%m-%d")
            
            new_file_name = new_date+'_'+m.group(1).strip()+'.mp3'
    
            if(not os.path.isfile(podcast_path+new_file_name)):
                downloadFile(url,podcast_path+new_file_name) 
            else:
                print new_file_name+" already exists, skipping!"
            print "\n"

#main app
parser = argparse.ArgumentParser(description='Podcast downloader.')
parser.add_argument('--username',help='username',required=True)
parser.add_argument('--password',help='password',required=True)
parser.add_argument('--url', default='http://lbc.audioagain.com/podcast.php?channel=subjames', help='url to podcast feed')

args = parser.parse_args()
print "Downloading podcast feed"
podcast_xml = downloadFileWithPassword(args.url,args.username,args.password)
print "Downloading podcasts"
downloadPodcasts(podcast_xml)
            