# +++++ ARD Mediathek Plugin for Plex v0.2.1 +++++
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
from core import *
from category import *
from mostViewedToday import *
from date import *

####################################################################################################

PLUGIN_TITLE = "ARD Mediathek"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART           = 'art.png'
ICON          = 'icon.png'

SHORT_CACHE_INTERVAL        = 300 #five minutes
CACHE_INTERVAL              = 1800 #half hour
LONG_CACHE_INTERVAL         = 604800 #one week
DEBUG                       = False

BASE_URL = "http://www.ardmediathek.de"

####################################################################################################


def Start():
  ObjectContainer.title1 = PLUGIN_TITLE
  ObjectContainer.art = R(ART)
  
  DirectoryObject.thumb = R(ICON)
  VideoClipObject.thumb = R(ICON)
  InputDirectoryObject.thumb = R(ICON)
  PrefsObject.thumb = R(ICON)
  NextPageObject.thumb = R(ICON)

@handler(VIDEO_PREFIX, PLUGIN_TITLE, thumb=ICON, art=ART)
def VideoMainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(MenuTopByDate), title="Nach Datum (Letzte 7 Tage)"))
  
  return oc

# def Start():
#   Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)
# 
#   Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
#   Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
#   
#   MediaContainer.art = R(ART)
#   MediaContainer.title1 = NAME
#   #DirectoryItem.thumb = R(ICON)
#     
# def VideoMainMenu():
#   dir = MediaContainer(viewGroup="List")
#   
#   dir.Append(Function(DirectoryItem(MenuTopByDate, title = "Nach Datum (Letzte 7 Tage)")))
#   dir.Append(Function(DirectoryItem(MenuTopMostViewedToday, title = "Beliebteste Sendungen (Heute)")))
#   dir.Append(Function(DirectoryItem(MenuCategories, title = "Kategorien")))
#   
#   return dir