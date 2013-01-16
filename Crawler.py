import sys
import requests
import BeautifulSoup
import urlparse
import signal
from optparse import OptionParser

def GetPage(url):
	try:
		REQ = requests.get(url, timeout = 2)
		if REQ.status_code==200:
			contentType = REQ.headers['Content-Type']
			if contentType.startswith('text/html'):
				return REQ.text
			else:
				return -1
		else:
			return 0
	except:
		print url + ' Please Check Url'
		return 0

def GetAnchorTags(html):
	parsedHtml = BeautifulSoup.BeautifulSoup(html)
	ATAGS = parsedHtml.findAll('a')
	return ATAGS

def GetProperLinks(aTags,currentUrl):
	LINKS = []
	for link in aTags:
		href = link.get('href')
		if href !=None:		
			if not href.startswith('http'):
				if not IsAbsUrl(href):
					href.lstrip('/')
					href = currentUrl + '/' + href
				if not href.startswith('mailto:'):
					LINKS.append(href)
			LINKS.append(href)
	return LINKS

def LinkCall(internalUrl,hrefs):
	LINKS = []
	for internalLinks in hrefs:
		if internalLinks.startswith(internalUrl):
			LINKS.append(internalLinks)
	return LINKS

def IsAbsUrl(url):
	return bool(urlparse.urlparse(url).scheme)

class Crawle:
	def __init__(self,values):
		self.url = values.url
		self.count = values.count
		self.ext = values.ext
		self.repo = []
		
	def CheckList(self,item):
		if item in self.repo:
			return 0
		return 1
	
	def StartCrawling(self,nextUrl=None):
		if nextUrl==None:
			nextUrl = self.url
		html = GetPage(nextUrl)
		if html !=0 and html !=-1:
			self.repo.append(nextUrl)
			self.DoPage(html,nextUrl)

	def Stop(self):
		if self.count==-1:
			return 1
		elif len(self.repo)<=self.count-1:
			return 1
		else:
			return 0

	def DoPage(self,html,currentUrl):
		if self.Stop()==1:
			if html != 0:
				anchorTags = GetAnchorTags(html)
				hrefs = GetProperLinks(anchorTags,self.url)
				if self.ext == 1:
					hrefs = LinkCall(self.url,hrefs)
				for href in hrefs:
					if self.CheckList(href)==1:
						self.StartCrawling(href)
			elif html == -1:
				print 'Invalid Content Type'
		else:
			self.View()
			sys.exit()
	
	def View(self):
		count = 1
		for elem in self.repo:
			print "%d.\t%s"%(count, elem)
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
