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

from core import *

####################################################################################################


TV_CLIP_FILTER = "clipFilter=fernsehen"

def MenuCategories(sender):
	dir = MediaContainer(viewGroup="List", title2=sender.itemTitle)
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
	# creates a list of all available show, clicking on a show will then list all episodes of this show
	dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
	
	url = url + "&" + TV_CLIP_FILTER
	site = XML.ElementFromURL(url, True)
	contentBoxes = site.xpath("//div[@class='mt-box']")
	Log('size contentBoxes: '+str(len(contentBoxes)))
	# the categories are in the second mt-box
	Log('contentBox[1]: ' +XML.StringFromElement(contentBoxes[1]))
	preloadElement = contentBoxes[1].xpath(".//a[@class='mt-box_preload']")[0]
	Log('preloadElement: ' +XML.StringFromElement(preloadElement))
	
	preloadUrl = FullURL(str(preloadElement.xpath("@href")[0]))
	Log('preloadUrl: '+preloadUrl)	
	AppendShowDirectoryItems(dir, preloadUrl)
	
	return dir
	
def AppendShowDirectoryItems(dir, url):
	site = XML.ElementFromURL(url, True)
	showElements = site.xpath("//div[@class='mt-media_item']")
	Log('showElements.size: '+str(len(showElements)))
	
	for i in range(0, len(showElements)):
		showElement = showElements[i]
		showLinkElements = showElement.xpath("./h3[@class='mt-title']/a")
		
		if (len(showLinkElements) > 0):
			showLinkElement = showLinkElements[0]
			
			#Log('showLinkElement'+XML.StringFromElement(showLinkElement))
		
			showUrl = str(showLinkElement.xpath("@href")[0])
			detailsUrl = str(showLinkElement.xpath("@rel")[0])
		
			showData = ParseShowData(FullURL(detailsUrl))
		
			if (showData is not None):
				dir.Append(
					Function(
						DirectoryItem(
							MenuByShow, 
							showData['showTitle'],
							showData['showChannel'],
							showData['showDescription'],
							FullURL(showData['thumbUrl'])
						), url = FullURL(showUrl)
					)
				)


# parse show informations, into a map
def ParseShowData(url):
	site = XML.ElementFromURL(url, True)
	
	titleElement = site.xpath("./h3[@class='mt-title']/a")[0]
	imgElement = site.xpath("./div[@class='mt-image']/img")[0]
	descElement = site.xpath("./p[@class='mt-description']")[0]
	channelElement = site.xpath("./p[@class='mt-channel']")[0]
	
	
	showTitle = Utf8Decode(titleElement.text.strip())
	showDescription = Utf8Decode(descElement.text.strip())
	showChannel = Utf8Decode(channelElement.text.strip())
	thumbUrl = str(imgElement.xpath("@src")[0])
	
	showDict = {
		'thumbUrl': thumbUrl,
		'showTitle': showTitle,
		'showChannel': showChannel,
		'showDescription': showDescription
	}
	
	return showDict
	
def MenuByShow(sender, url):
	Log('MenuByShow Called: sender['+str(sender)+'],ur['+str(url)+']')
	
	dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
	
	# two step of preloadPaths must be passed
	# step 1
	site = XML.ElementFromURL(url, True)
	preloadLinkPaths = site.xpath("//a[@class='mt-box_preload mt-box-overflow']/@href")
	# preloadLinkPaths[0] is for show related podcasts
	# preloadLinkPaths[1] is for show 'next upcomming livestream'
	# preloadLinkPaths[2] is for list of episodes of the show 'Titel-Liste'
	Log('preLoadLinkPaths leg: '+str(len(preloadLinkPaths)))
	# step 2
	site = XML.ElementFromURL(FullURL(preloadLinkPaths[2]), True)
	preloadLinkPaths = site.xpath("//a[@class='mt-box_preload']/@href")
	
	site = XML.ElementFromURL(FullURL(preloadLinkPaths[0]), True)
	showElements = site.xpath("//div[@class='mt-media_item']")
	
	for i in range(0, len(showElements)):
		showElement = showElements[i]
		showData = ParseEpisodeData(showElement)
		if (showData is not None):
			dir.Append(GetVideoItem(showData, False))
	
	return dir