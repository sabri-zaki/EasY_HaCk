#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Infoga: Email Information Gathering
#
# @url: https://github.com/m4ll0k/Infoga
# @author: Momo Outaadi (M4ll0k)
#
# Infoga is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3 of the License.
#
# Infoga is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Infoga; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from core.lib import http 
from core.lib import parser

class google:
	con = http.http()
	def __init__(self,target):
		self.target = target
		self.results = ""

	def search(self):
		try:
			url = "http://www.google.com/search?num=500&start=50&hl=en&meta=&q=%40\""+self.target+"\""
			resp = self.con.request(url)
			self.results += resp
		except Exception as error:
			pass

	def getemail(self):
		email = parser.parser(self.results,self.target)
		return email.email()

	def process(self):
		self.search()