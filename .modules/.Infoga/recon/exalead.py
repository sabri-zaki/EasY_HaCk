#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
#
# @name   : Infoga - Email Information Gathering
# @url    : http://github.com/m4ll0k
# @author : Momo Outaadi (m4ll0k)

from lib.output import *
from lib.request import *
from lib.parser import *

class Exalead(Request):
	def __init__(self,target):
		Request.__init__(self)
		self.target = target

	def search(self):
		test('Searching "%s" in Exalead...'%(self.target))
		url = "http://www.exalead.com/search/web/results/?q=%40{target}&elements_per_page=50&start_index=0".format(
			target=self.target)
		try:
			resp = self.send(
				method = 'GET',
				url = url,
				headers = {
							'Host':'www.exalead.com',
							'Referer':'http://exalead.com/search/web/results/?q=%40{target}'.format(
								target=self.target)
							}
				)
			return self.getemail(resp.content,self.target)
		except Exception as e:
			pass

	def getemail(self,content,target):
		return parser(content,target).email()