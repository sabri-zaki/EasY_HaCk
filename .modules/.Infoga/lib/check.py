#!/usr/bin/env python3
from lib.output import *
from urllib.parse import urlparse

def checkTarget(target):
	o = urlparse(target)
	if o.netloc == "":
		if "www." in o.path: return o.path.split('www.')[1]
		return o.path
	elif o.netloc != "":
		if "www." in o.netloc: return o.netloc.split("www.")[1]
		return o.netloc
	else: return target

def checkEmail(email):
	if '@' not in email:
		exit(warn('Invalid email %s'%email))
	return email

def checkSource(source):
	list_source = ['all','ask','baidu','google','bing',
	               'dogpile','exalead','jigsaw','pgp','yahoo'
	               ]
	if source not in list_source:
		exit(warn('Invalid search engine: %s'%source))
	return source

def checkVerbose(ver):
	verb = int(ver)
	if   verb == 0: return 1
	elif verb == 1: return 1
	elif verb == 2: return 2
	else: return 3