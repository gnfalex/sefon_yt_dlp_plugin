# ⚠ Don't use relative imports
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import get_elements_text_and_html_by_attribute, get_elements_html_by_attribute, extract_attributes, determine_ext
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
        for songname_div in get_elements_html_by_attribute("class", "song_name", webpage, tag = "div"):
            for songname_t, songname_h in get_elements_text_and_html_by_attribute("href",".*", songname_div, tag="a",escape_value=False):
                songname_href= extract_attributes(songname_h).get("href")
                out["entries"].append({
                    "_type":"url", 
                    "ie_key":"SefonMP3", 
                    "url":urljoin(url,songname_href),
                    "id":os.path.basename(songname_href[0:-1]).split("-")[0] ,
                    "title":songname_t
                 })
        for nextpage_ul in get_elements_html_by_attribute("class", "[^'\"]*next[^'\"]*", webpage, tag="ul", escape_value=False):
            for nextpage_a in get_elements_html_by_attribute("href", ".*", nextpage_ul, tag ="a", escape_value=False):
                nextpage_href = extract_attributes(nextpage_a).get("href")
                if len (nextpage_href) > 1:
                    out["entries"].extend(self._real_extract(urljoin(url, nextpage_href)).get("entries"))
        return out

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
        for protected_item in get_elements_html_by_attribute("class", "[^'\"]*url_protected[^'\"]*", webpage, tag="a", escape_value=False):
            protected_attrs = extract_attributes(protected_item)
            if all([bool(x in protected_attrs) for x in ["href", "data-mp3_id"]]):
                song_url = decodeUrl(protected_attrs.get("href"), protected_attrs.get("data-key"))
                song_url = urljoin(url, song_url)
                song_url2 = self._request_webpage(HEADRequest(song_url), mp3_id)
                song_name = unquote(os.path.basename(urlparse (song_url2.url).path))
                return {
                    "url": song_url2.url,
                    "direct": True,
                    "ext": determine_ext(song_name),
                    "id": mp3_id,
                    "title" : os.path.splitext(song_name)[0]
                }