#!/usr/bin/python

# Console colors
N  = '\033[0m'    # normal
H  = '\033[1;32m' # green
Y  = '\033[1;33m' # yellow
W  = '\033[1;37m' # white
R  = '\033[1;32m' # red


import json 
import os 
import sys 
import getopt 
import socket
import re 
import requests
import urlparse
from core.lib import http
from core.lib import parser 
from core.lib import colors 
from core.lib import printer
from core.recon import google
from core.recon import bing
from core.recon import pgp
from core.recon import yahoo
from core.recon import netcraft
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class Infoga(object):
	color = colors.colors()
	printf = printer.printer()
	allemail = []
	def banner(self):
		print self.color.red(1)+"   __        ___                         "+self.color.reset()
		print self.color.red(1)+"  |__.-----.'  _.-----.-----.---.-.      "+self.color.reset()
		print self.color.red(1)+"  |  |     |   _|  _  |  _  |  _  |      "+self.color.reset()
		print self.color.red(1)+"  |__|__|__|__| |_____|___  |___._|      "+self.color.reset()
		print self.color.red(1)+"                      |_____|            "+self.color.reset()
		print self.color.white(0)+"                                       "+self.color.reset()
		print self.color.white(0)+ R + "|| Infoga - Email Information Gathering"+self.color.reset()
		print self.color.white(0)+ R + "|| Infoga v4.1 ------> Alpha Team DZ          "+self.color.reset()
		print self.color.white(0)+ R + "|| SABRI ZAKI               "+self.color.reset()
		print self.color.white(0)+ R + "|| www.facebook.com/sabri.zaki.31  "+self.color.reset()
		print self.color.white(0)+"                                       "+self.color.reset()

	def usage(self):
		name = os.path.basename(sys.argv[0]).split(".")[0]
		self.banner()
		print "Usage: %s -t [target] -s [source]\n"%(name)
		print "\t-t --target\tDomain to search"
		print "\t-s --source\tData source: [all,google,bing,yahoo,pgp]"
		print "\t-i --info\tGet email informatios"
		print "\t-h --help\tShow this help and exit\n"
		print "Examples:"
		print "\t %s --target site.com --source all"%(name)
		print "\t %s --target site.com --source [google,bing,...]"%(name)
		print "\t %s --info test123@site.com"%(name)
		print ""
		sys.exit()

	def info(self):
		if self.allemail == []:
			self.printf.error("Not found email :(")
			sys.exit(0)
		allemail = []
		for x in self.allemail:
			if x not in allemail:
				allemail.append(x)
		try:
			for x in range(len(allemail)):
				self.printf.plus("Email: %s"%(allemail[x]))
				data = {'lang':'en'}
				data['email'] = allemail[x]
				req = requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
				req = requests.post("http://mailtester.com/testmail.php",data=data,verify=False)
				regex = re.compile("[0-9]+(?:\.[0-9]+){3}")
				ip = regex.findall(req.content)
				new = []
				for e in ip:
					if e not in new:
						new.append(e)
				for s in range(len(new)):
					req = requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
					req = requests.get("https://api.shodan.io/shodan/host/"+new[s]+"?key=UNmOjxeFS2mPA3kmzm1sZwC0XjaTTksy",verify=False)
					jso = json.loads(req.content,"utf-8")
					try:
						self.sock = socket.gethostbyaddr(new[s])[0]
					except  socket.herror as err:
						try:
							self.sock = jso["hostnames"][0]
						except KeyError as err:
							pass
					if "country_code" and "country_name" in jso:
						self.printf.ip("IP: %s (%s)"%(new[s],self.sock))
						self.printf.info("Country: %s (%s)"%(jso["country_code"],jso["country_name"]))
						self.printf.info("City: %s (%s)"%(jso["city"],jso["region_code"]))
						self.printf.info("ASN: %s"%(jso["asn"]))
						self.printf.info("ISP: %s"%(jso["isp"]))
						self.printf.info("Geolocation: %s"%("https://www.google.com/maps/@%s,%s,9z"%(jso["latitude"],jso["longitude"])))
						self.printf.info("Hostname: %s"%(jso["hostnames"][0]))
						self.printf.info("Organization: %s"%(jso["org"]))
						self.printf.info("Ports: %s"%(jso["ports"]))
						if "vulns" in jso:
							self.printf.info("Vulns: %s"%(jso["vulns"][0]))
						print ""

					elif "No information available for that IP." or "error" in jso:
						self.printf.ip("IP: %s (%s)"%(new[s],self.sock))
						self.printf.info("No information available for that ip :(",color="r")
						print ""
					else:
						self.printf.ip("IP: %s (%s)"%(new[s],self.sock))
						print ""
		except Exception as error:
			pass 
		sys.exit()

	def checkurl(self,url):
		scheme = urlparse.urlsplit(url).scheme
		netloc = urlparse.urlsplit(url).netloc
		path = urlparse.urlsplit(url).path
		if netloc == "":
			if path.startswith("www."):
				return path.split("www.")[1]
			else:
				return path
		if netloc != "":
			if netloc.startswith("www."):
				return netloc.split("www.")[1]
			else:
				return netloc

	def checkemail(self,email):
		if '@' not in email:
			self.banner()
			sys.exit(self.printf.error("Invalid email! Check your email"))
		return email

	def getinfo(self,email):
		self.printf.test("Checking email info...")
		try:
			data = {'lang':'en'}
			data['email'] = email 
			req = requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
			req = requests.post("http://mailtester.com/testmail.php",data=data,verify=False)
			regex = re.compile("[0-9]+(?:\.[0-9]+){3}")
			ip = regex.findall(req.content)
			new = []
			for e in ip:
				if e not in new:
					new.append(e)
			self.printf.plus("Email: %s"%email)
			for s in range(len(new)):
				req = requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
				req = requests.get("https://api.shodan.io/shodan/host/"+new[s]+"?key=UNmOjxeFS2mPA3kmzm1sZwC0XjaTTksy",verify=False)
				jso = json.loads(req.content)
				try:
					self.sock = socket.gethostbyaddr(new[s])[0]
				except socket.herror as err:
					try:
						self.sock = jso["hostnames"][0]
					except KeyError as err:
						pass
				if "country_code" and "country_name" in jso:
					self.printf.ip("IP: %s (%s)"%(new[s],self.sock))
					self.printf.info("Country: %s (%s)"%(jso["country_code"],jso["country_name"]))
					self.printf.info("City: %s (%s)"%(jso["city"],jso["region_code"]))
					self.printf.info("ASN: %s"%(jso["asn"]))
					self.printf.info("ISP: %s"%(jso["isp"]))
					self.printf.info("Geolocation: %s"%("https://www.google.com/maps/@%s,%s,9z"%(jso["latitude"],jso["longitude"])))
					self.printf.info("Hostname: %s"%(jso["hostnames"][0]))
					self.printf.info("Organization: %s"%(jso["org"]))
					self.printf.info("Ports: %s"%(jso["ports"]))
					if 'vulns' in jso:
						self.printf.info("Vulns: %s"%(jso["vulns"][0]))
					print ""
				
				elif "No information available for that IP." or "error" in jso:
					self.printf.ip("IP: %s (%s)"%(new[s],self.sock))
					self.printf.info("No information available for that ip :(",color="r")
					print ""

				else:
					self.printf.ip("IP: %s (%s)"%(new[s],self.sock))
		except Exception as error:
			pass
		sys.exit()

	def main(self,kwargs):
		if len(sys.argv) <= 1:
			self.usage()
		try:
			opts,args = getopt.getopt(kwargs,"t:s:i:h:",["target=","source=","info=","help"])
		except Exception as error:
			self.usage()
		for opt,arg in opts:
			if opt in ("-t","--target"):
				self.target = self.checkurl(arg) 
			if opt in ("-s","--source"):
				source = arg
				if source not in ("all","google","bing","yahoo","pgp"):
					self.banner()
					sys.exit(self.printf.error("Invalid search engine! Try with: all, google, bing, yahoo or pgp"))
				self.banner()
				netcraft.netcraft(self.target).search()
				if source == "google":
					self.google()
					self.info()
				elif source == "bing":
					self.bing()
					self.info()
				elif source == "yahoo":
					self.yahoo()
					self.info()
				elif source == "pgp":
					self.pgp()
					self.info()
				elif source == "all":
					self.all()
					self.info()
			if opt in ("-i","--info"):
				email = self.checkemail(arg)
				self.banner()
				self.getinfo(email)
			if opt in ("-h","--help"):
				self.usage()

	def google(self):
		self.printf.test("Searching \"%s\" in Google..."%(self.target))
		search = google.google(self.target)
		search.process()
		emails = search.getemail()
		self.allemail.extend(emails)

	def bing(self):
		self.printf.test("Searching \"%s\" in Bing..."%(self.target))
		search = bing.bing(self.target)
		search.process()
		emails = search.getemail()
		self.allemail.extend(emails)

	def yahoo(self):
		self.printf.test("Searching \"%s\" in Yahoo..."%(self.target))
		search = yahoo.yahoo(self.target)
		search.process()
		emails = search.getemail()
		self.allemail.extend(emails)

	def pgp(self):
		self.printf.test("Searching \"%s\" in Pgp..."%(self.target))
		search = pgp.pgp(self.target)
		search.process()
		emails = search.getemail()
		self.allemail.extend(emails)

	def all(self):
		self.google()
		self.bing()
		self.yahoo()
		self.pgp()

if __name__ == "__main__":
	try:
		Infoga().main(sys.argv[1:])
	except KeyboardInterrupt:
		sys.exit("CTRL+C.... :(")
