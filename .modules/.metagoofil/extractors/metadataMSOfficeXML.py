import unzip
import zipfile
import sys
import re
import os
import random
import myparser

class metaInfoMS:
	def __init__(self):
		self.template =""
		self.totalTime =""
		self.pages =""
		self.words =""
		self.characters =""
		self.application =""
		self.docSecurity =""
		self.lines =""
		self.paragraphs =""
		self.scaleCrop =""
		self.company =""
		self.linksUpToDate =""
		self.charactersWithSpaces =""
		self.shareDoc =""
		self.hyperlinksChanged =""
		self.appVersion =""	
		self.title =""
		self.subject =""
		self.creator =""
		self.keywords =""
		self.lastModifiedBy =""
		self.revision =""
		self.createdDate =""
		self.modifiedDate =""			
		self.userscomments =""
		self.thumbnailPath =""
		self.comments= "ok"
		self.text=""
		
	def __init__(self,filepath):
		self.template =""
		self.totalTime =""
		self.pages =""
		self.words =""
		self.characters =""
		self.application =""
		self.docSecurity =""
		self.lines =""
		self.paragraphs =""
		self.scaleCrop =""
		self.company =""
		self.linksUpToDate =""
		self.charactersWithSpaces =""
		self.shareDoc =""
		self.hyperlinksChanged =""
		self.appVersion =""	
		self.title =""
		self.subject =""
		self.creator =""
		self.keywords =""
		self.lastModifiedBy =""
		self.revision =""
		self.createdDate =""
		self.modifiedDate =""			
		self.thumbnailPath =""	
		rnd  = str(random.randrange(0, 1001, 3))
		zip = zipfile.ZipFile(filepath, 'r')
		file('app'+rnd+'.xml', 'w').write(zip.read('docProps/app.xml'))
		file('core'+rnd+'.xml', 'w').write(zip.read('docProps/core.xml'))
		file('docu'+rnd+'.xml', 'w').write(zip.read('word/document.xml'))
		try:
			file('comments'+rnd+'.xml', 'w').write(zip.read('word/comments.xml'))
			self.comments="ok"
		except:
			self.comments="error"
		thumbnailPath = ""
		#try:
			#file('thumbnail'+rnd+'.jpeg', 'w').write(zip.read('docProps/thumbnail.jpeg'))
		 	#thumbnailPath = 'thumbnail'+rnd+'.jpeg'
		#except:
		#	pass
			
		zip.close()
		# primero algunas estadisticas del soft usado para la edicion y del documento
		f = open ('app'+rnd+'.xml','r')
		app = f.read()
		self.cargaApp(app)
		f.close()
		if self.comments=="ok":
			f = open ('comments'+rnd+'.xml','r')
			comm = f.read()
			self.cargaComm(comm)
			f.close()
		
		# document content
		f = open ('docu'+rnd+'.xml','r')
		docu = f.read()
		self.text = docu
		f.close()
		# datos respecto a autor, etc

		f = open ('core'+rnd+'.xml','r')
		core = f.read()
		self.cargaCore(core)
		self.thumbnailPath = thumbnailPath
		f.close()

		# borramos todo menos el thumbnail
		
		os.remove('app'+rnd+'.xml')
		os.remove('core'+rnd+'.xml')	
		os.remove('comments'+rnd+'.xml')	
		os.remove('docu'+rnd+'.xml')
		#self.toString()
		
	def toString(self):
		print "--- Metadata app ---"
		print " template: " + str(self.template)
		print " totalTime: " + str(self.totalTime)
		print " pages: "+ str(self.pages)
		print " words: "+ str(self.words)
		print " characters: "+ str(self.characters)
		print " application: "+ str(self.application)
		print " docSecurity: "+ str(self.docSecurity)
		print " lines: "+ str(self.lines)
		print " paragraphs: "+ str(self.paragraphs)
		print " scaleCrop: " + str(self.scaleCrop)
		print " company: "+ str(self.company)
		print " linksUpToDate: " + str(self.linksUpToDate)
		print " charactersWithSpaces: "+ str(self.charactersWithSpaces)
		print " shareDoc:" + str(self.shareDoc)
		print " hyperlinksChanged:" + str(self.hyperlinksChanged)		
		print " appVersion:" + str(self.appVersion)

		print "\n --- Metadata core ---"
		print " title:" + str(self.title)
		print " subject:" + str(self.subject)
		print " creator:" + str(self.creator)
		print " keywords:" + str(self.keywords)
		print " lastModifiedBy:" + str(self.lastModifiedBy)
		print " revision:" + str(self.revision)
		print " createdDate:" + str(self.createdDate)
		print " modifiedDate:" + str(self.modifiedDate)
				
		print "\n thumbnailPath:" + str(self.thumbnailPath)
	
	def cargaComm(self,datos):
		try:
			p = re.compile('w:author="(.*?)" w')
			self.userscomments = p.findall(datos)
		except:
			pass

	
	def cargaApp(self,datos):
		try:
			p = re.compile('<Template>(.*)</Template>')
			self.template = str (p.findall(datos)[0])
		except:
			pass

		try:
			p = re.compile('<TotalTime>(.*)</TotalTime>')
			self.totalTime = str (p.findall(datos)[0])
		except:
			pass

		try:
			p = re.compile('<Pages>(.*)</Pages>')
			self.pages = str (p.findall(datos)[0])
		except:
			pass	
			
		try:
			p = re.compile('<Words>(.*)</Words>')
			self.words = str (p.findall(datos)[0])
		except:
			pass

		try:
			p = re.compile('<Characters>(.*)</Characters>')
			self.characters = str (p.findall(datos)[0])
		except:
			pass

		try:
			p = re.compile('<Application>(.*)</Application>')
			self.application = str (p.findall(datos)[0])
		except:
			pass		
			
		try:
			p = re.compile('<DocSecurity>(.*)</DocSecurity>')
			self.docSecurity = str (p.findall(datos)[0])
		except:
			pass			

		try:
			p = re.compile('<Lines>(.*)</Lines>')
			self.lines = str (p.findall(datos)[0])
		except:
			pass	
			
		try:
			p = re.compile('<Paragraphs>(.*)</Paragraphs>')
			self.paragraphs = str (p.findall(datos)[0])
		except:
			pass			

		try:
			p = re.compile('<ScaleCrop>(.*)</ScaleCrop>')
			self.scaleCrop = str (p.findall(datos)[0])
		except:
			pass	

		try:
			p = re.compile('<Company>(.*)</Company>')
			self.company = str (p.findall(datos)[0])
		except:
			pass	
	
		try:
			p = re.compile('<LinksUpToDate>(.*)</LinksUpToDate>')
			self.linksUpToDate = str (p.findall(datos)[0])
		except:
			pass
		
		try:
			p = re.compile('<CharactersWithSpaces>(.*)</CharactersWithSpaces>')
			self.charactersWithSpaces = str (p.findall(datos)[0])
		except:
			pass

		try:
			p = re.compile('<SharedDoc>(.*)</SharedDoc>')
			self.sharedDoc = str (p.findall(datos)[0])
		except:
			pass

		try:
			p = re.compile('<HyperlinksChanged>(.*)</HyperlinksChanged>')
			self.hyperlinksChanged = str (p.findall(datos)[0])
		except:
			pass

		try:
			p = re.compile('<AppVersion>(.*)</AppVersion>')
			self.appVersion = str (p.findall(datos)[0])
		except:
			pass
			
	def cargaCore(self,datos):
		try:
			p = re.compile('<dc:title>(.*)</dc:title>')
			self.title = str (p.findall(datos)[0])
		except:
			pass
		
		try:
			p = re.compile('<dc:subject>(.*)</dc:subject>')
			self.subject = str (p.findall(datos)[0])
		except:
			pass
		
		try:
			p = re.compile('<dc:creator>(.*)</dc:creator>')
			self.creator = str (p.findall(datos)[0])
		except:
			pass
		
		try:
			p = re.compile('<cp:keywords>(.*)</cp:keywords>')
			self.keywords = str (p.findall(datos)[0])
		except:
			pass
		
		try:
			p = re.compile('<cp:lastModifiedBy>(.*)</cp:lastModifiedBy>')
			self.lastModifiedBy = str (p.findall(datos)[0])
		except:
			pass
		
		try:
			p = re.compile('<cp:revision>(.*)</cp:revision>')
			self.revision = str (p.findall(datos)[0])
		except:
			pass
		
		try:
			p = re.compile('<dcterms:created xsi:type=".*">(.*)</dcterms:created>')
			self.createdDate = str (p.findall(datos)[0])
		except:
			pass
		
		try:
			p = re.compile('<dcterms:modified xsi:type=".*">(.*)</dcterms:modified>')
			self.modifiedDate = str (p.findall(datos)[0])
		except:
			pass		
	
	def getData(self):
		return "ok"
	
	def getTexts(self):
		return "ok"

	def getRaw(self):
		raw = "Not implemented yet"
		return raw

	def getUsers(self):
		res=[]
		temporal=[]
		res.append(self.creator)
		res.append(self.lastModifiedBy)
		if self.comments == "ok":
			res.extend(self.userscomments)
		else:
			pass
		for x in res:
			if temporal.count(x) ==0:
				temporal.append(x)
			else:
				pass
		return temporal

	def getEmails(self):
		res=myparser.parser(self.text)
		return res.emails()

	def getPaths(self):
		res=[]
		#res.append(self.revision)
		return res

	def getSoftware(self):
		res=[]
		res.append(self.application)
		return res
