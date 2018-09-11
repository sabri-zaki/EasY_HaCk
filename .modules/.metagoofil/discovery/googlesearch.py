import string
import httplib, sys
import myparser
import re
import time

class search_google:
	def __init__(self,word,limit,start,filetype):
		self.word=word
		self.results=""
		self.totalresults=""
		self.filetype=filetype
		self.server="www.google.com"
		self.hostname="www.google.com"
		self.userAgent="(Mozilla/5.0 (Windows; U; Windows NT 6.0;en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6"
		self.quantity="100"
		self.limit=limit
		self.counter=start
		
	def do_search_files(self):
		h = httplib.HTTP(self.server)
		h.putrequest('GET', "/search?num="+self.quantity+"&start=" + str(self.counter) + "&hl=en&meta=&q=filetype:"+self.filetype+"%20site:" + self.word)
		h.putheader('Host', self.hostname)
		h.putheader('User-agent', self.userAgent)	
		h.endheaders()
		returncode, returnmsg, headers = h.getreply()
		self.results = h.getfile().read()
		self.totalresults+= self.results

	def get_emails(self):
		rawres=myparser.parser(self.totalresults,self.word)
		return rawres.emails()
	
	def get_hostnames(self):
		rawres=myparser.parser(self.totalresults,self.word)
		return rawres.hostnames()
	
	def get_files(self):
		rawres=myparser.parser(self.totalresults,self.word)
		return rawres.fileurls()
	
	def process_files(self):
		while self.counter < self.limit:
			self.do_search_files()
			time.sleep(1)
			self.counter+=100
			print "\tSearching "+ str(self.counter) + " results..."

