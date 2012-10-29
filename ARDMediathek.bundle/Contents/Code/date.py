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
#from PMS import *
#from PMS.Objects import *
#from PMS.Shortcuts import *
from core import *

####################################################################################################


@route(VIDEO_PREFIX + "/recent")
def MenuTopByDate():
  oc = ObjectContainer()
  #dir = MediaContainer(viewGroup="List", title2=sender.itemTitle)
  site = HTML.ElementFromURL(BASE_URL)
  
  listPath = str(site.xpath("//ul[@class='mt_navi']/li[@class='special']/a/@href")[0])
  listURL = FullURL(listPath)

  for item in ParseMenuTopByDate(listURL):
    oc.add(item)

  return oc


def ParseMenuTopByDate(url):
  shows = []
  site = HTML.ElementFromURL(url)

  dateElements = site.xpath("//div[@id='mt-broadcast_date']/ol/li/a")
  for i in range(0, len(dateElements)):
    dateElement = dateElements[i]
    datePath = str(dateElement.xpath("@href")[0])
    dateWeekday = dateElement.xpath("./span")[0].text
    dateDate = dateElement.xpath("./strong")[0].text

    shows.append(DirectoryObject(key=Callback(MenuByDate, url=FullURL(datePath)), title=dateWeekday + " - " + dateDate))

  return shows

@route(VIDEO_PREFIX + "/date")
def MenuByDate(url):
  oc = ObjectContainer()
  site = HTML.ElementFromURL(url)
  
  listPath = str(site.xpath("//a[@class='mt-box_pillbutton']/@href")[0])
  listURL = FullURL(listPath)
  
  site = HTML.ElementFromURL(listURL)
  for showElement in site.xpath("//div[@class='mt-box-overflow']/ol/li/ol/li/div[@class='mt-media_item']"):
    showData = ParseEpisodeData(showElement)
    if (showData is not None):
      oc.add(GetVideoItem(showData))
  
  return oc