# ⚠ Don't use relative imports
from yt_dlp.extractor.common import InfoExtractor
import re
import base64
from urllib.parse import urlparse, unquote, urljoin
import os
from yt_dlp.networking import HEADRequest, Request
# ℹ️ If you need to import from another plugin
# from yt_dlp_plugins.extractor.example import ExamplePluginIE

# ℹ️ Instructions on making extractors can be found at:
# 🔗 https://github.com/yt-dlp/yt-dlp/blob/master/CONTRIBUTING.md#adding-support-for-a-new-site


def decodeUrl (url, key):
    url = url[1:]
    for x in key[::-1]:
        url = x.join(url.split(x)[::-1])
    return base64.b64decode(url).decode()

# ⚠ The class name must end in "IE"
class SefonArtistIE(InfoExtractor):
    _WORKING = True
    _VALID_URL = r'^https?://sefon.pro/artist/(?P<id>\d+)-.*'

    def _real_extract(self, url):
         artist_id = self._match_id(url)
         webpage = self._download_webpage (url, artist_id)
         out = {"_type":"playlist", "id":artist_id, "entries":[]}
         import lxml.html
         html_parsed = lxml.html.document_fromstring(webpage)
         for songname in html_parsed.xpath("//div[contains(@class,'song_name')]/a"):
             out["entries"].append({"_type":"url", "ie_key":"SefonMP3", "url":"https://sefon.pro"+songname.attrib["href"], "id":os.path.basename(songname.attrib["href"][0:-1]).split("-")[0] ,"title":songname.text})
         for nextpage in html_parsed.xpath("//ul[contains(@class,'next')]/li/a/@href"):
             print (nextpage)
             if "/" in nextpage:
               addout = self._real_extract(urljoin(url, nextpage))
               out["entries"].extend(addout["entries"])
         return (out)
        
class SefonCollectionIE(SefonArtistIE):
    _WORKING = True
    _VALID_URL = r"https?://sefon.pro/collections/.*/(?P<id>\d+)-.*"

class SefonMP3IE(SefonArtistIE):
    _WORKING = True
    _VALID_URL = r"https?://sefon.pro/mp3/(?P<id>\d+)-.*"
    def _real_extract (self, url):
      upurl = ""
      mp3_id = self._match_id(url)
      webpage = self._download_webpage (url, mp3_id)
      try:
          import lxml.htmlee
          html_parsed = lxml.html.document_fromstring(webpage)
          for song in html_parsed.xpath("//a[url_protected and href and data-mp3_id]"):
              
              upurl = decodeUrl(song.attrib("href"), song.attrib("data-key"))
      except:
        match = re.search(r'<a[^>]*url_protected[^>]*href="(?P<purl>[^"]*)"[^>]*data-key="(?P<pkey>[^"]*)"[^>]*data-mp3_id[^>]*>', webpage)
        if match:
          upkey = [x for x in match.group("pkey")]
          upkey.reverse()
          upurl = match.group("purl")[1:]
        for k in upkey:
            upurl = upurl.split(k)
            upurl.reverse()
            upurl = k.join(upurl)
        #upurl = decodeUrl (match.group("purl"), match.group("pkey"))      
        upurl = base64.b64decode(upurl).decode()
      upurl = urljoin (url, upurl)
      hdurl = self._request_webpage(HEADRequest(upurl), mp3_id)
      fname = unquote(os.path.basename(urlparse (hdurl.url).path))
      return {
            "url": hdurl.url,
            "direct": True,
            "ext": os.path.splitext(fname)[1][1:],
            "id": mp3_id,
            "title" : os.path.splitext(fname)[0]
        }