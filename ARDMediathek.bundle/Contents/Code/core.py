# +++++ ARD Mediathek Plugin for Plex v0.1.1 alpha +++++
#
# (C) 2010 by Sebastian Majstorovic
# 
# Licensed under the GPL, Version 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#    http://www.gnu.org/licenses/gpl-3.0-standalone.html
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

####################################################################################################

VIDEO_PREFIX = "/video/ardmediathek"
BASE_URL = "http://www.ardmediathek.de"

def FullURL(path):
  return BASE_URL + path

def video_items(url):
  return [MediaObject(parts=[PartObject(key=Callback(GetStreamURL, url=url))])]

def GetVideoItem(showData, includeShowName=True):
  showDetails = showData['showDetails']
  if (includeShowName):
    itemTitle = showData['showName'] + " | " + showData['showTitle']
  else:
    itemTitle = showData['showTitle']

  url = FullURL(showData['showPath'])
  return EpisodeObject(key=Callback(GetStreamURL, url=url),
      rating_key=url,
      title = itemTitle,
      #subtitle = showDetails['showDuration'],
      thumb = FullURL(showDetails['showThumbPath']),
      summary = showDetails['showDescription'],
      items=video_items(url),
      )

def ParseEpisodeData(element):
  titleElements = element.xpath("./h3[@class='mt-title']/a")
  videoTypeElements = element.xpath(".//span[" + containing("mt-icon_video") + "]")
  if ((len(titleElements) > 0) and (len(videoTypeElements) > 0)):
    showPath = str(titleElements[0].xpath("@href")[0])
    documentID = GetDocumentID(showPath)

    showTitle = Utf8Decode(titleElements[0].text).strip()    
    showDetails = ParseEpisodeDetails(element, documentID)
    showName = ParseEpisodeName(element).strip()

    itemDict = {
      'showPath': showPath,
      'documentID': documentID,
      'showTitle': showTitle,
      'showName': showName,
      'showDetails': showDetails
    }

    return itemDict

  return None

def ParseEpisodeName(element):
  nameElement = element.xpath(".//p[" + containing("mt-source") + "]")[0]
  reShowName = re.search("aus:(.*)", nameElement.text)
  showName = Utf8Decode(reShowName.group(1))

  return showName

def containing(className):
  return "contains(concat(' ',normalize-space(@class),' '),' " + className + " ')";

def ParseEpisodeDetails(detailPage, documentID):

  titleElements = detailPage.xpath("./h3[@class='mt-title']/a")
  showTitle = Utf8Decode(titleElements[0].text)
  showPath = str(titleElements[0].xpath("@href")[0])
  
  showThumbPath = str(detailPage.xpath(".//img/@src")[0])  
  durationElement = detailPage.xpath(".//span[@class='mt-airtime']")[0]
  # actually: this regex does nothing more, than stripping the durationElement.text after the string 'min'
  # as sometimes, this string is not contained, the regex result must be checked
  reShowDuration = re.search(".* min", durationElement.text)
  if (reShowDuration is not None):
	showDuration = Utf8Decode(reShowDuration.group(0))
  else:
	showDuration = durationElement.text

  nameElement = detailPage.xpath(".//p[" + containing("mt-source") + "]")[0]
  reShowName = re.search("aus:(.*)", nameElement.text)
  #seems to not used anymore, so it's no problem to do this
  showName = "" #Utf8Decode(reShowName.group(1))

  # In the new layout, the detail flyover only contains the descriptive text
  detailPage = HTML.ElementFromURL(FullURL("/ard/servlet/ajax-cache/" + documentID + "/view=ajax/index.html"))
  descriptionElement = detailPage.xpath(".//p")[0]
  showDescription = Utf8Decode(descriptionElement.text)

  detailPageDict = {
    'showTitle': showTitle,
    'showPath': showPath,
    'showThumbPath': showThumbPath,
    'showDuration': showDuration,
    'showName': showName,
    'showDescription': showDescription
  }

  return detailPageDict

def Utf8Decode(source):
  try:
      return source.encode("iso-8859-1").decode("utf-8")
  except:
      return ""

@route(VIDEO_PREFIX + "/getstreamurl")
@indirect
def GetStreamURL(url):
  site = HTML.ElementFromURL(url)

  scriptContainer = site.xpath("//div[@class='mt-player_container']/script")[0]
  scriptText = scriptContainer.text

  # e.g. mediaCollection.addMediaStream(0, 0, "rtmp://vod.daserste.de/ardfs/", "mp4:videoportal/mediathek/Verbotene+Liebe/c_260000/264588/format326035.mp4?sen=Verbotene+Liebe&amp;for=Web-S&amp;clip=Folge+4171+Nur+die+Wahrheit+z%E4hlt&amp;mediathek=ardmediathek", "default");
  reStream = re.findall("addMediaStream\(\d,\s*\d,\s*\"(.*)\",\s*\"(.*)\",\s*\"(.*)\"\)", scriptText)  

  streamsCount = len(reStream) - 1
  if (streamsCount < 0):
    streamsCount = 0
  # take the 'last' mediaStream, which is usually the highest quality
  streamParts = reStream[streamsCount]
  streamBase = streamParts[0]
  streamClip = streamParts[1]

  # cut get parameters from the clip url
  if (streamClip.find("?") > -1):
  	streamClip = streamClip[0:streamClip.find("?")]
  
  return IndirectResponse(VideoClipObject, key=RTMPVideoURL(url=streamBase, clip=streamClip))


def GetDocumentID(path):
  reDocumentID = re.search("ajax-cache\/(\d+)\/view", path)
  if (reDocumentID is None):
    reDocumentID = re.search("documentId=(\d+)", path)
  if (reDocumentID is None):
    reDocumentID = re.search("content\/(\d+)\?datum", path)
  documentID = reDocumentID.group(1)

  return documentID

def GetLargeThumb(documentID):
  site = HTML.ElementFromURL("http://www.ardmediathek.de/ard/servlet/ajax-cache/" + documentID + "/view=ajax/index.html")
  imagePath = str(site.xpath("//img/@src")[0])

  return HTTP.Request(FullURL(imagePath))

def ParseMediaItemList(url):
  shows = []
  site = HTML.ElementFromURL(url)
  showElements = site.xpath("//div[@class='mt-media_item']")
  Log('showElements.size: '+str(len(showElements)))
  for i in range(0, len(showElements)):
    showElement = showElements[i]
    showData = ParseEpisodeData(showElement)
    if (showData is not None):
      shows.append(GetVideoItem(showData))
  return shows