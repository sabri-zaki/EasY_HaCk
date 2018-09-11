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
from core.lib import printer
import re 

class netcraft:
	con = http.http()
	printf = printer.printer()
	def __init__(self,target):
		self.target = target

	def search(self):
		self.printf.test("Searching \"%s\" hostnames..."%(self.target))
		try:
			url = "http://searchdns.netcraft.com/?restriction=site+contains&host=%s&lookup=wait..&position=limited"%(self.target)
			resp = self.con.urllib(url,None)
			if resp:
				sites = re.findall('url=\S+"',resp,re.I)
				if sites:
					self.printf.plus("Found %s sites"%(len(sites)))
					print ""
					for x in range(len(sites)):
						host = sites[x].split('"')[0]
						print " - %s"%(host.split("url=")[1])
					print ""
				else:
					self.printf.error("Not found hostnames")
		except Exception as error:
			pass