#!/usr/bin/env python3
# -*- coding:utf-8 -*- 

import urllib3
import requests
from lib.output import *

class Request(object):
	agent = ''
	def send(self,method,url,params=None,data=None,headers=None):
		if headers is None: headers={}
		headers['User-Agent'] = Request.agent
		try:
			session = requests.Session()
			req = urllib3.disable_warnings(
				urllib3.exceptions.InsecureRequestWarning
				)
			req = requests.request(
				method = method.upper(),
				url = url,
				params = params,
				data = data,
				allow_redirects = True,
				verify = False  )
			return req
		except Exception as e:
			exit(warn('Failed to establish a new connection'))