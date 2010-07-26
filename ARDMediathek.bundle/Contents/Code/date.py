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

def MenuTopByDate(sender):
  dir = MediaContainer(viewGroup="List")
  site = XML.ElementFromURL(BASE_URL, True)
  
  listPath = str(site.xpath("//ul[@class='mt_navi']/li[@class='special']/a/@href")[0])
  listURL = FullURL(listPath)

  menuItems = ParseMenuTopByDate(listURL)
  for i in range(0, len(menuItems)):
    dir.Append(menuItems[i])

  return dir


def ParseMenuTopByDate(url):
  shows = []
  site = XML.ElementFromURL(url, True)

  dateElements = site.xpath("//div[@id='mt-broadcast_date']/ol/li/a")
  for i in range(0, len(dateElements)):
    dateElement = dateElements[i]
    datePath = str(dateElement.xpath("@href")[0])
    dateWeekday = dateElement.xpath("./span")[0].text
    dateDate = dateElement.xpath("./strong")[0].text

    shows.append(Function(
      DirectoryItem(
        MenuByDate, 
        title = dateWeekday + " - " + dateDate
      ), url = FullURL(datePath)
    ))

  return shows


def MenuByDate(sender, url):
  dir = MediaContainer(viewGroup="InfoList")
  site = XML.ElementFromURL(url, True)
  
  listPath = str(site.xpath("//a[@class='mt-box_pillbutton']/@href")[0])
  listURL = FullURL(listPath)
  
  site = XML.ElementFromURL(listURL, True)
  showElements = site.xpath("//div[@class='mt-box-overflow']/ol/li/ol/li/div[@class='mt-media_item']")
  for i in range(0, len(showElements)):
    showElement = showElements[i]
    showData = ParseShowData(showElement)
    if (showData is not None):
      dir.Append(GetVideoItem(showData))
  
  return dir