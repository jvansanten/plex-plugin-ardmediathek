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

@route(VIDEO_PREFIX + "/categories")
def MenuCategories():
	oc = ObjectContainer()
	site = HTML.ElementFromURL(BASE_URL)
	
	Log('Testoutput')
	for categorieItem in site.xpath("//div[@class='mt-reset mt-categories']/ul/li/a"):
		itemPath = str(categorieItem.xpath("@href")[0])
		itemText = categorieItem.text
		oc.add(DirectoryObject(key=Callback(MenuByCategory, url=FullURL(itemPath)), title=itemText))
		
	return oc

@route(VIDEO_PREFIX + "/category")
def MenuByCategory(url):
	# creates a list of all available show, clicking on a show will then list all episodes of this show
	dir = ObjectContainer()
	
	url = url + "&" + TV_CLIP_FILTER
	site = HTML.ElementFromURL(url)
	contentBoxes = site.xpath("//div[@class='mt-box']")
	Log('size contentBoxes: '+str(len(contentBoxes)))
	# the categories are in the second mt-box
	Log('contentBox[1]: ' +XML.StringFromElement(contentBoxes[1]))
	preloadElement = contentBoxes[1].xpath(".//a[@class='mt-box_preload']")[0]
	Log('preloadElement: ' +XML.StringFromElement(preloadElement))
	
	preloadUrl = FullURL(str(preloadElement.xpath("@href")[0]))
	Log('preloadUrl: '+preloadUrl)
	i = 0
	while preloadUrl is not None:
		preloadUrl = AppendShowDirectoryItems(dir, preloadUrl)
		Log.Debug("preloadUrl is now %s", preloadUrl)
		i += 1
		if i > 10:
			j
	
	return dir
	
def AppendShowDirectoryItems(dir, url):
	site = HTML.ElementFromURL(url)
	
	Log.Debug("Parsing page: %s", url)
	for showElement in site.xpath("//div[@class='mt-media_item']"):
		AppendShowData(dir, showElement)
	links = site.xpath("//a[" + containing("ajax-paging")+ " and contains(., 'Weiter')]/@href")
	if len(links) > 0:
		return FullURL(links[-1])
	else:
		return None

# parse show informations, into a map
def AppendShowData(dir, showElement):
	showLinkElements = showElement.xpath("./h3[@class='mt-title']/a")
	if len(showLinkElements) == 0:
		return None
	else:
		showLinkElement = showLinkElements[0]
	showUrl = str(showLinkElement.xpath("@href")[0])
	detailsUrl = str(showLinkElement.xpath("@rel")[0])
	
	titleElement = showElement.xpath("./h3[@class='mt-title']/a")[0]
	imgElement = showElement.xpath("./div[@class='mt-image']/img")[0]
	channelElement = showElement.xpath(".//span[@class='mt-channel']")[0]
	
	detailElement = HTML.ElementFromURL(FullURL(detailsUrl))
	descElement = detailElement.xpath("./p[@class='mt-description']")[0]
	
	showTitle = Utf8Decode(titleElement.text.strip())
	showDescription = Utf8Decode(descElement.text.strip())
	showChannel = Utf8Decode(channelElement.text.strip())
	thumbUrl = str(imgElement.xpath("@src")[0])
	
	showData = {
		'thumbUrl': thumbUrl,
		'showTitle': showTitle,
		'showChannel': showChannel,
		'showDescription': showDescription
	}
	
	url = FullURL(showUrl)
	dir.add(TVShowObject(key=Callback(MenuByShow, url=url), rating_key=url,
	    title=showData['showTitle'], studio=showData['showChannel'],
	    summary=showData['showDescription'], thumb=FullURL(showData['thumbUrl'])))

@route(VIDEO_PREFIX + "/show")
def MenuByShow(url):
	
	dir = ObjectContainer()
	
	# two step of preloadPaths must be passed
	# step 1
	site = HTML.ElementFromURL(url)
	preloadLinkPaths = site.xpath("//a[@class='mt-box_preload mt-box-overflow']/@href")
	# preloadLinkPaths[0] is for show related podcasts
	# preloadLinkPaths[1] is for show 'next upcomming livestream'
	# preloadLinkPaths[2] is for list of episodes of the show 'Titel-Liste'
	Log('preLoadLinkPaths leg: '+str(len(preloadLinkPaths)))
	# step 2
	site = HTML.ElementFromURL(FullURL(preloadLinkPaths[2]))
	preloadLinkPaths = site.xpath("//a[@class='mt-box_preload']/@href")
	
	site = HTML.ElementFromURL(FullURL(preloadLinkPaths[0]))
	for showElement in site.xpath("//div[@class='mt-media_item']"):
		showData = ParseEpisodeData(showElement)
		if (showData is not None):
			dir.add(GetVideoItem(showData, False))
	
	return dir