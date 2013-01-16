import sys
import requests
import BeautifulSoup
import urlparse
import signal
from optparse import OptionParser

#Getting Requested Page
def GetPage(url):
	try:
		REQ = requests.get(url, timeout = 2)
		if REQ.status_code==200:
			contentType = REQ.headers['Content-Type']
			if contentType.startswith('text/html'):
				return REQ.text
			else:
				return -5
	
	except requests.ConnectionError:
		return -1
	except requests.Timeout:
		return -2
	except requests.HTTPError:
		return -3
	except requests.RequestException:
		return -4
		
	return 0

def GetTag(html,tag='a'):
	#Getting Content Residing Under Given Tags
	parsedHtml = BeautifulSoup.BeautifulSoup(html)
	VALUES = parsedHtml.findAll(tag)
	return VALUES

def GetProperLinks(tag,currentUrl,option='href'):
	#Extracting Links From Tags
	LINKS = []
	for link in tag:
		href = link.get(option)
		if href !=None:		
			if not href.startswith('http'):
				if not IsAbsUrl(href):
					href.lstrip('/')
					href = currentUrl + '/' + href
				if not href.startswith('mailto:'):
					LINKS.append(href)
			LINKS.append(href)
	return LINKS

def GetAllLinks(html,url):
	#Merging Links List Fetched From Anchor,IFrame,Frame Tags
	LinkTags = GetTag(html,'a')
	hrefs = GetProperLinks(LinkTags,url,'href')
	LinkTags = GetTag(html,'iframe')
	isrcs = GetProperLinks(LinkTags,url,'src')
	LinkTags = GetTag(html,'frame')
	srcs = GetProperLinks(LinkTags,url,'src')
	LINKS = hrefs + isrcs + srcs
	return LINKS

def LinkCall(internalUrl,hrefs):
	#Removing External Links
	#By Base Path - Input URL
	LINKS = []
	for internalLinks in hrefs:
		if internalLinks.startswith(internalUrl):
			LINKS.append(internalLinks)
	return LINKS

def IsAbsUrl(url):
	return bool(urlparse.urlparse(url).scheme)

def RequestIssue(issue):
	if issue == -1:
		return 'Network Issue'
	elif issue == -2:
		return 'TimeOut'
	elif issue == -3:
		return 'Bad/Invalid HTTP Response'
	elif issue == -4:
		return 'Something Weird'
	elif issue == -5:
		return 'Content Type'
	return 'Fetched'

class Crawle:
	def __init__(self,values):
		#Setting Options Values
		self.url = values.url
		self.count = values.count
		self.ext = values.ext
		self.repo = []
		
	def CheckList(self,item):
		#Checking Current Crawled URL's Against Repo To Avoid Duplicates
		for value in self.repo:
			if value[0]==item:
				return 0
		return 1
	
	def StartCrawling(self,nextUrl=None):
		if nextUrl==None:
			nextUrl = self.url
		html = GetPage(nextUrl)
		
		if html == -2:
			html = GetPage(nextUrl)
		
		value = [nextUrl,1]
		if type(html)==type(1):
			value[1] = html
			self.repo.append(value)
		else:
			self.repo.append(value)
			self.DoPage(html,nextUrl)

	def Stop(self):
		#Decides When To Stop
		if self.count==-1:
			return 1
		elif len(self.repo)<=self.count-1:
			return 1
		else:
			return 0

	def DoPage(self,html,currentUrl):
		if self.Stop()==1:
			links = GetAllLinks(html,self.url)
			if self.ext == 1:
				links = LinkCall(self.url,links)
			for link in links:
				if self.CheckList(link)==1:
					self.StartCrawling(link)
		else:
			self.View()
			sys.exit()
	
	def View(self):
		#Displaying Crawled URL's
		count = 1
		print 'SRNO.\tURL\t\t\t\t'
		for elem in self.repo:
			print "%d.\t%s\t\t\t\t%s"%(count,elem[0],RequestIssue(elem[1]))
			count += 1
	
	def cleanup(*args):
		self.View()
		sys.exit()

if __name__ == '__main__':
    parser = OptionParser(usage=__doc__, version="Crawle")
    parser.add_option('-u', action='store', dest='url',type='string', default='')
    parser.add_option('-c', action='store', dest='count',type='int', default=-1)
    parser.add_option('-e', action='store', dest='ext',type='int', default=0)
    params, args = parser.parse_args(sys.argv)

if params.url != '':
	if not params.url.startswith('http'):
		params.url = 'http://' + params.url
	CrawleOb = Crawle(params)
	CrawleOb.StartCrawling()
	CrawleOb.View()
	
	#Catching Kill/Stop Script Signals
	signal.signal(signal.SIGINT, CrawleOb.cleanup)
	signal.signal(signal.SIGTERM, CrawleOb.cleanup)
	
else:
	print 'No Input Given'
