#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
#
# @name   : Infoga - Email Information Gathering
# @url    : http://github.com/m4ll0k
# @author : Momo Outaadi (m4ll0k)

from lib.output import *
from lib.request import *
from lib.parser import *

class Baidu(Request):
	def __init__(self,target):
		Request.__init__(self)
		self.target = target

	def search(self):
		test('Searching "%s" in Baidu...'%(self.target))
		url = "http://www.baidu.com/s?wd=%40{target}&pn=0".format(
			target=self.target)
		try:
			resp = self.send(
				method = 'GET',
				url = url,
				headers = {
							'Host':'www.baidu.com'
				}
				)
			return self.getemail(resp.content,self.target)
		except Exception as e:
			pass

	def getemail(self,content,target):
		return parser(content,target).email()