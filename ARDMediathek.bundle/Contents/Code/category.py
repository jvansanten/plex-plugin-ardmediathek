# +++++ ARD Mediathek Plugin for Plex  +++++
#
# (C) 2010 by Robert Kleinschmager
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


TV_CLIP_FILTER = "clipFilter=fernsehen"

def MenuCategories(sender):
	dir = MediaContainer(viewGroup="List")
	site = XML.ElementFromURL(BASE_URL, True)
	
	categorieItems = site.xpath("//div[@class='mt-reset mt-categories']/ul/li/a")
	Log('Testoutput')
	for i in range(0, len(categorieItems)):
		categorieItem = categorieItems[i]
		itemPath = str(categorieItem.xpath("@href")[0])
		itemText = categorieItem.text
		dir.Append(Function(
			DirectoryItem(
			MenuByCategory, 
			title = itemText
			), url = FullURL(itemPath)
		))
	return dir

def MenuByCategory(sender, url):
	
	dir = MediaContainer(viewGroup="InfoList")
	
	url = url + "&" + TV_CLIP_FILTER
	site = XML.ElementFromURL(url, True)
	contentBoxes = site.xpath("//div[@class='mt-box']")
	# the categories are in the second mt-box
	categoryBox = contentBoxes[1]
	Log('categoryBox '+str(categoryBox))
	#showElements = categoryBox.xpath(".//div[@class='mt-media_item']")
	
	showElements = site.xpath("(//div[@class='mt-box'])[2]//div[@class='mt-media_item']")
	Log('showElements size '+str(len(showElements)))
	
	for i in range(0, len(showElements)):
		showElement = showElements[i]
		showData = ParseShowData(showElement)
		Log('looping showElements '+i, false)
		if (showData is not None):
			dir.Append(GetVideoItem(showData))
	return dir
