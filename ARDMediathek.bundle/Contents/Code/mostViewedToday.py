# +++++ ARD Mediathek Plugin for Plex  +++++
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

# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
from core import *

####################################################################################################

def MenuTopMostViewedToday(sender):
  dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
  site = XML.ElementFromURL(BASE_URL, True)
  
  contentBoxes = site.xpath("//div[@class='mt-box']")
  mostViewedBox = contentBoxes[1]
  mostViewedElement = mostViewedBox.xpath(".//div[@class='mt-box_header']/ul/li/a")[1]
  listPath = str(mostViewedElement.xpath('@href')[0])
  Log('ListPath: '+listPath)

  documentID = GetDocumentID(listPath)
  listURL = FullURL("/ard/servlet/ajax-cache/" + documentID + "/view=list/show=recent/index.html")

  menuItems = ParseMenuTopMostViewedToday(listURL)
  for i in range(0, len(menuItems)):
    dir.Append(menuItems[i])
  
  return dir


def ParseMenuTopMostViewedToday(url):
  shows = []
  site = XML.ElementFromURL(url, True)
  showElements = site.xpath("//div[@class='mt-media_item']")
  for i in range(0, len(showElements)):
    showElement = showElements[i]
    showData = ParseEpisodeData(showElement)
    if (showData is not None):
      shows.append(GetVideoItem(showData))
  return shows