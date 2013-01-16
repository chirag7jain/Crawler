# Assumptions
# Web Page -- ContentType text/html
# Links Contained In --- Anchor,Frame,IFrame Tags

#System Libraries
import sys
import gc
import signal
import logging
from datetime import datetime

#3rd Party Libraries
import requests
from optparse import OptionParser
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup

def GetPage(url):
	#Getting Requested Page
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
	except:
		return -6
	return 0

def GetTag(html,tag='a'):
	#Getting Content Residing Under Given Tags
	try:
		parsedHtml = BeautifulSoup(html)
		VALUES = parsedHtml.findAll(tag)
		return VALUES
	except Exception as e:
		logging.error('Date - %s Exception - %s /n Content - %s /n Content %s',datetime.now(),e,type(html),html)
		return None

def GetProperLinks(tag,currentUrl,option='href'):
	#Extracting Links From Tags
	LINKS = []
	for link in tag:
		href = link.get(option)
		if CheckLinkProtocol(href)==1:
			LINKS.append(CheckUrl(href,currentUrl))
	return LINKS

def GetAllLinks(html,url):
	#Merging Links List Fetched From Anchor,IFrame,Frame Tags
	tagLinkSource = [['a','href'],['iframe','src'],['frame','src']]
	LINKS = []
	for source in tagLinkSource:
		LinkTags = GetTag(html,source[0])
		if LinkTags != None:
			hyperlinks = GetProperLinks(LinkTags,url,source[1])
			LINKS += hyperlinks
	return LINKS

def LinkCall(internalUrl,hrefs):
	#Removing External Links
	#By Base Path - Input URL
	LINKS = []
	for internalLinks in hrefs:
		if internalLinks.startswith(internalUrl):
			LINKS.append(internalLinks)
	return LINKS

def RequestIssue(issue):
	#Return Issue Type
	if issue == -1:
		return 'Network Issue'
	elif issue == -2:
		return 'TimeOut'
	elif issue == -3:
		return 'Bad/Invalid HTTP Response'
	elif issue == -4:
		return 'Something Weird'
	elif issue == -5:
		return 'Bad Content Type'
	elif issue == -6:
		return 'Unknowm'
	return 'Fetched'

def CheckLinkProtocol(link):
	#Checking For UnCrawalable Protocols
	if link !=None:
		protocols = ['ftp','file','gopher','hdl','imap','mailto','mms','news','nntp','prospero','rsync','rtsp','rtspu','sftp','shttp','sip','sips','snews','svn','svn+ssh','telnet','wais','#']
		for protocol in protocols:
			if link.startswith(protocol):
				return 0
		return 1
	return 0

def CheckUrl(URL,baseurl):
	#Checking URL
	#Converting Relative URL to Absolute URL
	urlCheck = urlparse(URL)
	if not (urlCheck.scheme).startswith('http'):
		if urlCheck.netloc == '':
			URL = URL.lstrip('/')
			URL = baseurl.rstrip('/') + '/' + URL
			return URL
		URL = 'http://' + URL
	return URL

def View(repo):
	#Displaying Crawled URLS
	count = 1
	print 'SRNO.\tURL\t\t\t\t'
	for elem in repo:
		print "%d.\t%s\t\t\t\t%s"%(count,elem[0],RequestIssue(elem[1]))
		count += 1

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
	
	def GettingResponse(self,URL):
		#Trying To Get URL Content
		RESPONSE = GetPage(URL)
		if RESPONSE == -2:
			RESPONSE = GetPage(URL)
		self.AddToRepo(URL,RESPONSE)
		return RESPONSE
	
	def AddToRepo(self,URL,response):
		#Adding Crawled URL To Repo
		value = [URL,response]
		self.repo.append(value)

	def StartCrawling(self,nextUrl=None):
		if nextUrl==None:
			nextUrl = self.url
		response = self.GettingResponse(nextUrl)
		self.DoPage(response,nextUrl)

	def Stop(self):
		#Decides When To Stop Crawling
		if self.count==-1:
			return 1
		elif len(self.repo)<=self.count-1:
			return 1
		else:
			self.CleanUp()

	def DoPage(self,html,currentUrl):
		#Scan Page For Links
		#Start Crawling The Link
		if self.Stop()==1:
			links = GetAllLinks(html,self.url)
			if self.ext == 1:
				links = LinkCall(self.url,links)
			for link in links:
				if self.CheckList(link)==1:
					self.StartCrawling(link)
	
	def CleanUp(self,signum=None,frame=None):
		#Stops The Script
		View(self.repo)
		sys.exit()

if __name__ == '__main__':
    parser = OptionParser(usage=__doc__, version="Crawle")
    parser.add_option('-u', action='store', dest='url',type='string', default='')
    parser.add_option('-c', action='store', dest='count',type='int', default=-1)
    parser.add_option('-e', action='store', dest='ext',type='int', default=0)
    params, args = parser.parse_args(sys.argv)

#Checking Value
if params.url != '':
	
	if params.count >= -1 and params.count !=0 and params.ext>=0 and params.ext<2:
			
		if not params.url.startswith('http'):
			params.url = 'http://' + params.url
		
		gc.enable()
		
		CrawleOb = Crawle(params)
		
		logging.basicConfig(format='%(levelname)s:%(message)s',filename='info.log',level=logging.ERROR)
		
		#Catching Kill/Stop Script Signals
		signal.signal(signal.SIGINT, CrawleOb.CleanUp)
		signal.signal(signal.SIGTERM, CrawleOb.CleanUp)
		
		CrawleOb.StartCrawling()
	
	else:
		print 'Please Check Your Input'
			
else:
	print 'No Input Given'
