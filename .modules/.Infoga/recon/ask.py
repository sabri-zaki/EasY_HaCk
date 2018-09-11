#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
#
# @name   : Infoga - Email Information Gathering
# @url    : http://github.com/m4ll0k
# @author : Momo Outaadi (m4ll0k)

from lib.output import *
from lib.request import *
from lib.parser import *

class Ask(Request):
	def __init__(self,target):
		Request.__init__(self)
		self.target = target

	def search(self):
		test('Searching "%s" in Ask...'%(self.target))
		url = "http://www.ask.com/web?q=%40{target}&pu=100&page=0".format(
			target=self.target)
		try:
			resp = self.send(
				method = 'GET',
				url = url
				)
			return self.getemail(resp.content,self.target)
		except Exception as e:
			print(e)

	def getemail(self,content,target):
		return parser(content,target).email()