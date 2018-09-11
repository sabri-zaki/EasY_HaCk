#!/usr/bin/env python
import sys, re, os, subprocess

class metaExtractor:
	def __init__(self,fname):
		self.fname=fname
		self.command="extract" #If any error put the full path
		self.data=""
		self.paths=[]
		self.users=[]


	def runExtract(self):
		comm=self.command+" "+self.fname
		try:
			process = subprocess.Popen([self.command,self.fname], shell=False, stdout=subprocess.PIPE)
			res=process.communicate()
			self.data=res[0]
			return "ok"
		except:
			return "error"

	def getData(self):
		pathre= re.compile('worked on .*')
		pathre2= re.compile('template -.*')
		for reg in (pathre,pathre2):
			path=reg.findall(self.data)
			if path !=[]:
				for x in path:
					try:
						temp=x.split('\'')[1]
						if self.paths.count(temp) == 0:
							self.paths.append(temp)
					except:
						pass

		author= re.compile(': Author \'.*\'')
		authors=author.findall(self.data)
		if authors !=[]:
			for x in authors:
				temp=x.split('\'')[1]
				temp=temp.replace('\'','')
				if self.users.count(temp) == 0:
					self.users.append(temp)

	def getUsers(self):
		return self.users

	def getPaths(self):
		return self.paths		
