from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.i18n import getTerminalCharset
from sys import argv, stderr, exit

class metaMs2k:
	def __init__(self,filename):
		self.filename=filename
		self.users=[]
		self.paths=[]
		self.software=[]
		self.modification=[]
		self.creationDate=[]
		self.lastPrinted=[]
		self.raw=""

	def getData(self):
		filename, realname = unicodeFilename(self.filename), self.filename
		try:
			parser = createParser(filename, realname)
		except:
			return "error"
		try:
			metadata = extractMetadata(parser)
		except HachoirError, err:
			print "Metadata extraction error: %s" % unicode(err)
			metadata = None
		if not metadata:
			print "Unable to extract metadata on file: " + self.filename
		else:
			text = metadata.exportPlaintext()
			charset = getTerminalCharset()
			for line in text:
				res=line.split(":")
				if res[0]=="- Author":
						self.users.append(res[1])
				elif res[1]==" Author:":
						self.users.append(res[2])
				elif res[0]=="- Producer":
						self.software.append(res[1])
				elif res[0]=="- Creation date":
						self.creationDate.append(res[1])
				elif res[0]=="- Last modification":
						self.modification.append(res[1])
				elif res[1]==" Template":
						xres= line.replace("- Comment: Template:","")
						self.paths.append(xres)
				elif res[1]==" LastSavedBy":
				#		print res[1] + res[2]
						self.users.append(res[2])
				elif res[1]==" LastPrinted":
						self.lastPrinted.append(res[2])
				elif res[0]=="- Revision history":
						#self.paths.append(res[2])
						res2=line.split(",")
						self.paths.append(res2[1].split("file ")[1])
				self.raw=text
		return "ok"

	def getUsers(self):
		return self.users
	def getSoftware(self):
		return self.software
	def getPaths(self):
		return self.paths
	def getRaw(self):
		return self.raw
