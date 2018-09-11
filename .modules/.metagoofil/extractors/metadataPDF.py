#!/usr/bin/env python
#
# metadataPDF.py - dump pdf metadata 
#
# Copy of Yusuke's dumppdf to add dumpmeta
import sys, re, os
from pdfminer.psparser import PSKeyword, PSLiteral
from pdfminer.pdfparser import PDFDocument, PDFParser
from pdfminer.pdftypes import PDFStream, PDFObjRef, resolve1, stream_value
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, process_pdf
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
import myparser


# dumpmeta
class metapdf:
	def __init__(self,fname, password=''):
		self.fname=fname
		self.password=password
		self.metadata=''
		self.users=[]
		self.software=[]
		self.paths=[]
		self.raw=""
		self.company=[]
		self.text=""
	
	def getTexts(self):
		try:
			password =''
			pagenos = set()
			maxpages = 0
			codec = 'utf-8'
			caching = True
			laparams = LAParams()
			rsrcmgr = PDFResourceManager(caching=caching)
			outfp = file('temppdf.txt','w')
			device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams)
			fname= self.fname
			fp = file(fname, 'rb')
			process_pdf(rsrcmgr, device, fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True)
			fp.close()
			device.close()
			outfp.close()
			infp = file('temppdf.txt','rb')
			test=infp.read()
			infp.close()
			os.remove('temppdf.txt')
			self.text=test
			return "ok"
		except Exception,e:
			return e

	def getData(self):
		doc = PDFDocument()
		fp = file(self.fname, 'rb')
		parser = PDFParser(fp)
		try:
			parser.set_document(doc)
			doc.set_parser(parser)
			doc.initialize(self.password)
		except:
			return "error"
		
		parser.close()
		fp.close()
		#try:
		#	metadata = resolve1(doc.catalog['Metadata'])
		#	return "ok"
		#except:
		#	print "[x] Error in PDF extractor, Metadata catalog"
		try:
			for xref in doc.xrefs:
				info_ref=xref.trailer.get('Info')
				if info_ref:
					info=resolve1(info_ref)
				self.metadata=info
				self.raw = info
			if self.raw == None:
				return "Empty metadata"
			else:
				return "ok"
		except Exception,e:
			return e 
			print "\t [x] Error in PDF extractor, Trailer Info"

	def getEmails(self):
		em=myparser.parser(self.text)
		return em.emails()
		
	def getHosts(self,domain):
		em=myparser.parser(self.text,domain)
		return em.hostnames()
		
	def getUsers(self):
		if self.metadata.has_key('Author'):
			self.users.append(self.metadata['Author'])
		return self.users	
	def getCompany(self):
		try:
			self.users.append(self.metadata['Company'])
		except:
			print "\t [x] Error in PDF metadata Company"	
		return self.company


	def getSoftware(self):
		try:
			self.software.append(self.metadata['Producer'])
		except:	
			print "\t [x] Error in PDF metadata Software"
		try:
			self.software.append(self.metadata['Creator'])
		except:
			print "\t [x] Error in PDF metadata Creator"
		return self.software

	def getPaths(self):
		return self.paths

	def getRaw(self):
		return self.raw
