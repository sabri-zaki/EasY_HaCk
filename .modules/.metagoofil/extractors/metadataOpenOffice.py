import unzip
import zipfile
import sys
import re
import os
import random

class metaInfoOO:
	def __init__(self):
		self.version =""
		self.generator=""
		self.creationDate=""
		self.date=""
		self.language=""
		self.editingCycles=""
		self.editingDuration=""
		self.tableCount=""
		self.imageCount=""
		self.objectCount=""
		self.pageCount=""
		self.paragraphCount=""
		self.wordCount=""
		self.characterCount=""
		self.initialCreator=""
		self.creator=""
		self.title=""
		self.description=""
		self.subject=""
		self.printedBy=""
		self.printDate=""	
			
	def __init__(self,filepath):
		self.version =""
		self.generator=""
		self.creationDate=""
		self.date=""
		self.language=""
		self.editingCycles=""
		self.editingDuration=""
		self.tableCount=""
		self.imageCount=""
		self.objectCount=""
		self.pageCount=""
		self.paragraphCount=""
		self.wordCount=""
		self.characterCount=""
		self.initialCreator=""
		self.creator=""
		self.title=""
		self.description=""
		self.subject=""
		self.printedBy=""
		self.printDate=""	
		
		rnd  = str(random.randrange(0, 1001, 3))
		zip = zipfile.ZipFile(filepath, 'r')
		file('meta'+rnd+'.xml', 'w').write(zip.read('meta.xml'))
		zip.close()

		# done, ahora a currar con el xml

		f = open ('meta'+rnd+'.xml','r')
		meta = f.read()
		self.carga(meta)
		f.close()
		os.remove('meta'+rnd+'.xml')

		
	def toString(self):
		print "--- Metadata ---"
		print " version: " + str(self.version)
		print " generator: " + str(self.generator)
		print " creation-date: "+ str(self.creationDate)
		print " date: "+ str(self.date)
		print " language: "+ str(self.language)
		print " editing cycles: "+ str(self.editingCycles)
		print " editing duration: "+ str(self.editingDuration)
		print " table count: "+ str(self.tableCount)
		print " image count: "+ str(self.imageCount)
		print " object count: " + str(self.objectCount)
		print " page count: "+ str(self.pageCount)
		print " paragraph count: " + str(self.paragraphCount)
		print " word count: "+ str(self.wordCount)
		print " character count:" + str(self.characterCount)
		print " initial creator:" + str(self.initialCreator)		
		print " creator:" + str(self.creator)
		print " title:" + str(self.title)
		print " description:" + str(self.description)
		print " subject:" + str(self.subject)
		print " printed by:" + str(self.printedBy)
		print " print date:" + str(self.printDate)
		
	def carga(self,datos):
		try:
			p = re.compile('office:version="([\d.]*)"><office:meta>')
			self.version = str (p.findall(datos)[0])
		except:
			pass
		try:	
			p = re.compile('<meta:generator>(.*)</meta:generator>')
			self.generator = str (p.findall(datos)[0])			
		except:
			pass

		try:			
			p = re.compile('<meta:creation-date>(.*)</meta:creation-date>')
			self.creationDate = str (p.findall(datos)[0])
		except:
			pass

		try:	
			p = re.compile('<dc:date>(.*)</dc:date>')
			self.date = str (p.findall(datos)[0])
		except:
			pass
			
		try:		
			p = re.compile('<dc:language>(.*)</dc:language>')
			self.language = str (p.findall(datos)[0])
		except:
			pass
			
		try:	
			p = re.compile('<meta:editing-cycles>(.*)</meta:editing-cycles>')
			self.editingCycles = str (p.findall(datos)[0])
		except:
			pass
			
		try:	
			p = re.compile('<meta:editing-duration>(.*)</meta:editing-duration>')
			self.editingDuration = str (p.findall(datos)[0])
		except:
			pass
			
		try:	
			p = re.compile('meta:table-count="(\d*)"')
			self.tableCount = str (p.findall(datos)[0])
		except:
			pass
			
		try:			
			p = re.compile('meta:image-count="(\d*)"')
			self.imageCount = str (p.findall(datos)[0])
		except:
			pass
			
		try:			
			p = re.compile('meta:object-count="(\d*)"')
			self.objectCount = str (p.findall(datos)[0])
		except:
			pass
			
		try:			
			p = re.compile('meta:page-count="(\d*)"')
			self.pageCount = str (p.findall(datos)[0])
		except:
			pass
			
		try:			
			p = re.compile('meta:paragraph-count="(\d*)"')
			self.paragraphCount = str (p.findall(datos)[0])
		except:
			pass
			
		try:			
			p = re.compile('meta:word-count="(\d*)"')
			self.wordCount = str (p.findall(datos)[0])
		except:
			pass
			
		try:			
			p = re.compile('meta:character-count="(\d*)"')
			self.characterCount = str (p.findall(datos)[0])
		except:
			pass
			
		try:			
			p = re.compile('<meta:initial-creator>(.*)</meta:initial-creator>')
			self.initialCreator = str (p.findall(datos,re.DOTALL)[0])
		except:
			pass
		
		try:			
			p = re.compile('<dc:creator>(.*)</dc:creator>')
			self.creator = str (p.findall(datos,re.DOTALL)[0])
		except:
			pass	

		try:			
			p = re.compile('<dc:title>(.*)</dc:title>')
			self.title = str (p.findall(datos)[0])
		except:
			pass			
		
		try:			
			p = re.compile('<dc:description>(.*)</dc:description>')
			self.description = str (p.findall(datos)[0])
		except:
			pass
		
		try:			
			p = re.compile('<dc:subject>(.*)</dc:subject>')
			self.subject = str (p.findall(datos)[0])
		except:
			pass

		try:	
			p = re.compile('<meta:printed-by>(.*)</meta:printed-by>')
			self.printedBy = str (p.findall(datos)[0])
		except:
			pass
		
		try:	
			p = re.compile('<meta:print-date>(.*)</meta:print-date>')
			self.printDate = str (p.findall(datos)[0])
		except:
			pass					
			
