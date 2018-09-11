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
import re
import string

class parser:

	def __init__(self,results,target):
		self.results = results
		self.target = target 

	def clean(self):
		self.results = re.sub("<em>", "", self.results)
		self.results = re.sub("<b>", "", self.results)
		self.results = re.sub("</b>", "", self.results)
		self.results = re.sub("</em>", "", self.results)
		self.results = re.sub("%2f", " ", self.results)
		self.results = re.sub("%3a", " ", self.results)
		self.results = re.sub("<strong>", "", self.results)
		self.results = re.sub("</strong>", "", self.results)
		self.results = re.sub("<wbr>", "", self.results)
		self.results = re.sub("</wbr>", "", self.results)
		
		for x in ('>', ':', '=', '<', '/', '\\', ';', '&', '%3A', '%3D', '%3C'):
			self.results = string.replace(self.results, x, " ")

	def email(self):
		self.clean()
		regex = re.compile('[a-zA-Z0-9.\-_+#~!$&\',;=:]+'+'@'+'[a-zA-Z0-9.-]*'+self.target)
		temp = regex.findall(self.results)
		emails = []
		for x in temp:
			if x not in emails:
				emails.append(x)
		return emails